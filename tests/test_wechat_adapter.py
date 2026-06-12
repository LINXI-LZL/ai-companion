import tempfile
import unittest
from pathlib import Path


class WeChatAdapterTests(unittest.TestCase):
    def test_normalizes_text_event_and_builds_outbound_message(self):
        from app.wechat_adapter import build_outbound_message, normalize_inbound_event

        inbound = normalize_inbound_event(
            {
                "FromUserName": "external-owner",
                "MsgType": "text",
                "Content": "老板又临下班改需求，真的离谱",
                "MsgId": "wechat-msg-1",
                "CreateTime": 1780648000,
            }
        )
        outbound = build_outbound_message(
            inbound,
            {
                "reply_text": "离谱，先骂一句再拆。",
                "mode": "text_plus_sticker",
                "sticker_intent": "sticker_speechless",
                "voice_intent": "none",
                "media": {"fallback_to_text": True},
            },
        )

        self.assertEqual(inbound["channel"], "wecom_kf")
        self.assertEqual(inbound["external_user_id"], "external-owner")
        self.assertEqual(inbound["content_type"], "text")
        self.assertEqual(inbound["content"], "老板又临下班改需求，真的离谱")
        self.assertEqual(outbound["channel"], "wecom_kf")
        self.assertEqual(outbound["external_user_id"], "external-owner")
        self.assertEqual(outbound["message_type"], "text")
        self.assertEqual(outbound["text"], "离谱，先骂一句再拆。")
        self.assertEqual(outbound["media_intent"], "sticker_speechless")
        self.assertTrue(outbound["fallback_to_text"])

    def test_mock_wechat_inbound_uses_companion_flow(self):
        from app.server import create_mock_wechat_response
        from app.storage import Storage

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_mock_wechat_response(
                store,
                {
                    "FromUserName": "external-owner",
                    "MsgType": "text",
                    "Content": "今天好累，但睡不着",
                    "MsgId": "wechat-msg-2",
                },
            )
            user = store.get_user_by_handle("wechat:external-owner")
            messages = store.list_messages(user["id"])

        self.assertEqual(response["inbound"]["content"], "今天好累，但睡不着")
        self.assertEqual(response["outbound"]["message_type"], "text")
        self.assertEqual(response["outbound"]["voice_intent"], "voice_sleepy_companion")
        self.assertEqual(len(messages), 1)
        self.assertIn("睡", messages[0]["reply_text"])

    def test_wecom_live_config_status_redacts_secret_values(self):
        from app.wecom_live import load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "super-secret-value",
                "WECOM_KF_TOKEN": "token-value",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
                "WECOM_CALLBACK_PUBLIC_URL": "https://example.com/api/wecom-live/callback",
            }
        )
        status = config.to_status()

        self.assertTrue(status["configured"])
        self.assertEqual(status["channel"], "wecom_live")
        self.assertTrue(status["ready_for_real_callback"])
        self.assertEqual(status["crypto_status"], "ready")
        self.assertEqual(status["send_mode"], "real_text_send")
        self.assertNotIn("super-secret-value", str(status))
        self.assertNotIn("token-value", str(status))
        self.assertEqual(status["fields"]["WECOM_KF_SECRET"], "set")
        self.assertEqual(status["public_callback_url"], "https://example.com/api/wecom-live/callback")

    def test_wecom_live_config_reports_missing_fields(self):
        from app.wecom_live import load_wecom_config_from_env

        status = load_wecom_config_from_env({"WECOM_CORP_ID": "ww-corp"}).to_status()

        self.assertFalse(status["configured"])
        self.assertIn("WECOM_KF_SECRET", status["missing_fields"])
        self.assertIn("WECOM_KF_TOKEN", status["missing_fields"])
        self.assertEqual(status["fields"]["WECOM_CORP_ID"], "set")

    def test_wecom_live_signature_uses_sorted_token_timestamp_nonce_encrypt(self):
        from app.wecom_live import build_wecom_signature, verify_wecom_signature

        signature = build_wecom_signature("token", "1700000000", "nonce", "encrypted")

        self.assertEqual(signature, "a976d3f9651ff9c34c56c6f9774c36bca10ec1de")
        self.assertTrue(verify_wecom_signature("token", "1700000000", "nonce", "encrypted", signature))
        self.assertFalse(verify_wecom_signature("token", "1700000000", "nonce", "tampered", signature))

    def test_wecom_live_callback_preflight_rejects_invalid_ciphertext(self):
        from app.wecom_live import handle_callback_validation, load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": "encrypted",
            "msg_signature": "a976d3f9651ff9c34c56c6f9774c36bca10ec1de",
        }

        result = handle_callback_validation(config, query)

        self.assertEqual(result["status"], "base64_invalid")
        self.assertTrue(result["signature_valid"])
        self.assertEqual(result["http_status"], 400)

    def test_wecom_aes_256_cbc_matches_nist_vector(self):
        from app.wecom_live import _aes_256_cbc_decrypt, _aes_256_cbc_encrypt

        key = bytes.fromhex("603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4")
        iv = bytes.fromhex("000102030405060708090a0b0c0d0e0f")
        plaintext = bytes.fromhex(
            "6bc1bee22e409f96e93d7e117393172a"
            "ae2d8a571e03ac9c9eb76fac45af8e51"
            "30c81c46a35ce411e5fbc1191a0a52ef"
            "f69f2445df4f9b17ad2b417be66c3710"
        )
        ciphertext = bytes.fromhex(
            "f58c4c04d6e5f1ba779eabfb5f7bfbd6"
            "9cfc4e967edb808d679f777bc6702c7d"
            "39f23369a9d9bacfa530e26304231461"
            "b2eb05e2c39be9fcda6c19078c6a9d1b"
        )

        self.assertEqual(_aes_256_cbc_encrypt(plaintext, key, iv), ciphertext)
        self.assertEqual(_aes_256_cbc_decrypt(ciphertext, key, iv), plaintext)

    def test_wecom_live_callback_validation_decrypts_real_echostr(self):
        from app.wecom_live import (
            build_wecom_signature,
            encrypt_wecom_message,
            handle_callback_validation,
            load_wecom_config_from_env,
        )

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        echostr = encrypt_wecom_message(
            aes_key,
            "url-check-ok",
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": echostr,
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", echostr),
        }

        result = handle_callback_validation(config, query)

        self.assertEqual(result["status"], "ok")
        self.assertTrue(result["signature_valid"])
        self.assertEqual(result["http_status"], 200)
        self.assertEqual(result["reply_text"], "url-check-ok")

    def test_wecom_live_callback_validation_does_not_require_secret_or_open_kfid(self):
        from app.wecom_live import (
            build_wecom_signature,
            encrypt_wecom_message,
            handle_callback_validation,
            load_wecom_config_from_env,
        )

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
            }
        )
        echostr = encrypt_wecom_message(
            aes_key,
            "url-check-ok",
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": echostr,
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", echostr),
        }

        result = handle_callback_validation(config, query)

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["reply_text"], "url-check-ok")
        self.assertEqual(config.to_status()["ready_for_real_callback"], True)

    def test_wecom_live_encrypted_callback_flow_uses_companion_and_ack(self):
        from app.server import create_wecom_live_callback_response
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<FromUserName><![CDATA[external-owner]]></FromUserName>"
            "<CreateTime>1780648000</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[老板又临下班改需求，真的离谱]]></Content>"
            "<MsgId>live-msg-3</MsgId>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><ToUserName><![CDATA[ww-corp]]></ToUserName><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(store, config, query, body)
            messages = store.list_messages()
            jobs = store.list_wecom_callback_jobs()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(response["inbound"]["channel"], "wecom_live")
        self.assertEqual(response["inbound"]["external_user_id"], "external-owner")
        self.assertEqual(response["inbound"]["content"], "老板又临下班改需求，真的离谱")
        self.assertEqual(messages, [])
        self.assertEqual(jobs[0]["status"], "queued")
        self.assertEqual(jobs[0]["job_type"], "direct_text")

    def test_wecom_live_direct_text_callback_sends_real_text_message(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<FromUserName><![CDATA[external-owner]]></FromUserName>"
            "<CreateTime>1780648000</CreateTime>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[老板又临下班改需求，真的离谱]]></Content>"
            "<MsgId>live-msg-4</MsgId>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }
        seen_requests = []

        def fake_transport(request):
            seen_requests.append(request)
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "send_msg":
                return {"errcode": 0, "errmsg": "ok", "msgid": "sent-msg-1"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(
                store,
                config,
                query,
                body,
                send_transport=fake_transport,
            )
            queued_requests = list(seen_requests)
            worker_result = process_next_wecom_live_job(store, config, send_transport=fake_transport)
            audit_events = store.list_audit_events()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(queued_requests, [])
        self.assertEqual(worker_result["status"], "done")
        self.assertEqual(worker_result["result"]["send_policy"], "real_text_send")
        self.assertEqual(worker_result["result"]["send_result"]["status"], "sent")
        self.assertEqual(worker_result["result"]["send_result"]["msgid"], "sent-msg-1")
        self.assertEqual(seen_requests[0]["name"], "get_access_token")
        self.assertEqual(seen_requests[1]["name"], "send_msg")
        self.assertIn("/cgi-bin/kf/send_msg?access_token=access-token", seen_requests[1]["url"])
        self.assertEqual(seen_requests[1]["json"]["touser"], "external-owner")
        self.assertEqual(seen_requests[1]["json"]["open_kfid"], "wkf-123")
        self.assertEqual(seen_requests[1]["json"]["msgtype"], "text")
        self.assertIn("站你这边", seen_requests[1]["json"]["text"]["content"])
        send_audit = [event for event in audit_events if event["event_type"] == "wecom_live_send_msg_success"][0]
        self.assertEqual(send_audit["payload"]["status"], "sent")
        self.assertEqual(send_audit["payload"]["msgid_present"], True)
        self.assertNotIn("access-token", str(send_audit["payload"]))
        self.assertNotIn("secret", str(send_audit["payload"]))
        self.assertNotIn("站你这边", str(send_audit["payload"]))

    def test_wecom_live_send_failure_is_acked_and_audited_without_secret_leak(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<FromUserName><![CDATA[external-owner]]></FromUserName>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[今天真的有点累]]></Content>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }

        def fake_transport(request):
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "send_msg":
                return {"errcode": 40003, "errmsg": "invalid touser"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(
                store,
                config,
                query,
                body,
                send_transport=fake_transport,
            )
            worker_result = process_next_wecom_live_job(store, config, send_transport=fake_transport)
            audit_events = store.list_audit_events()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(worker_result["result"]["send_policy"], "payload_only")
        self.assertEqual(worker_result["result"]["send_result"]["status"], "send_msg_failed")
        send_audit = [event for event in audit_events if event["event_type"] == "wecom_live_send_msg_failure"][0]
        self.assertEqual(send_audit["payload"]["status"], "send_msg_failed")
        self.assertEqual(send_audit["payload"]["reason"], "send_msg_failed")
        self.assertEqual(send_audit["payload"]["msgtype"], "text")
        self.assertNotIn("access-token", str(send_audit["payload"]))
        self.assertNotIn("secret", str(send_audit["payload"]))
        self.assertNotIn("今天真的有点累", str(send_audit["payload"]))

    def test_wecom_live_failed_callback_records_safe_audit(self):
        from app.server import create_wecom_live_callback_response
        from app.storage import Storage
        from app.wecom_live import load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
            }
        )
        query = {"timestamp": "1700000000", "nonce": "nonce", "msg_signature": "bad"}
        body = "<xml><ToUserName><![CDATA[ww-corp]]></ToUserName></xml>"

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(store, config, query, body)
            audit_events = store.list_audit_events()

        self.assertEqual(response["status"], "encrypt_missing")
        self.assertEqual(response["http_status"], 400)
        self.assertFalse(response["body_has_encrypt"])
        self.assertEqual(audit_events[0]["event_type"], "wecom_live_callback_failure")
        payload = audit_events[0]["payload"]
        self.assertEqual(payload["status"], "encrypt_missing")
        self.assertEqual(payload["http_status"], 400)
        self.assertFalse(payload["signature_valid"])
        self.assertFalse(payload["body_has_encrypt"])
        self.assertNotIn("token", str(payload).lower())
        self.assertNotIn("abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG", str(payload))

    def test_wecom_live_extracts_encrypt_from_namespaced_and_form_wrapped_xml(self):
        from app.wecom_live import extract_encrypt_from_xml, parse_wecom_xml

        body = (
            "xml=%EF%BB%BF%3Cxml%20xmlns%3Awx%3D%22urn%3Awechat%22%3E"
            "%3Cwx%3AToUserName%3E%3C%21%5BCDATA%5Bww-corp%5D%5D%3E%3C%2Fwx%3AToUserName%3E"
            "%3Cwx%3AEncrypt%3E%3C%21%5BCDATA%5Bencrypted-value%5D%5D%3E%3C%2Fwx%3AEncrypt%3E"
            "%3C%2Fxml%3E"
        )

        self.assertEqual(extract_encrypt_from_xml(body), "encrypted-value")
        parsed = parse_wecom_xml(body)
        self.assertEqual(parsed["Encrypt"], "encrypted-value")
        self.assertEqual(parsed["ToUserName"], "ww-corp")

    def test_wecom_live_kf_msg_event_is_acked_and_audited_without_message(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<CreateTime>1780648000</CreateTime>"
            "<MsgType><![CDATA[event]]></MsgType>"
            "<Event><![CDATA[kf_msg_or_event]]></Event>"
            "<Token><![CDATA[pull-token]]></Token>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(store, config, query, body)
            worker_result = process_next_wecom_live_job(store, config)
            audit_events = store.list_audit_events()
            messages = store.list_messages()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(worker_result["result"]["status"], "sync_msg_deferred")
        self.assertEqual(worker_result["result"]["send_policy"], "ack_only")
        self.assertEqual(messages, [])
        sync_audit = [event for event in audit_events if event["event_type"] == "wecom_live_sync_msg_deferred"][0]
        self.assertEqual(sync_audit["payload"]["event"], "kf_msg_or_event")
        self.assertEqual(sync_audit["payload"]["message_token_present"], True)
        self.assertNotIn("pull-token", str(sync_audit["payload"]))

    def test_wecom_live_kf_msg_event_syncs_text_message_into_companion(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<CreateTime>1780648000</CreateTime>"
            "<MsgType><![CDATA[event]]></MsgType>"
            "<Event><![CDATA[kf_msg_or_event]]></Event>"
            "<Token><![CDATA[pull-token]]></Token>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }
        seen_requests = []

        def fake_transport(request):
            seen_requests.append(request)
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "sync_msg":
                return {
                    "errcode": 0,
                    "next_cursor": "next-cursor",
                    "has_more": 0,
                    "msg_list": [
                        {
                            "msgid": "sync-msg-1",
                            "open_kfid": "wkf-123",
                            "external_userid": "external-owner",
                            "send_time": 1780648001,
                            "msgtype": "text",
                            "text": {"content": "老板又临下班改需求，真的离谱"},
                        }
                    ],
                }
            if request["name"] == "send_msg":
                return {"errcode": 0, "errmsg": "ok", "msgid": "sent-sync-msg-1"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(store, config, query, body, sync_transport=fake_transport)
            queued_requests = list(seen_requests)
            worker_result = process_next_wecom_live_job(store, config, sync_transport=fake_transport)
            user = store.get_user_by_handle("wechat:external-owner")
            messages = store.list_messages(user["id"])
            audit_events = store.list_audit_events()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(queued_requests, [])
        self.assertEqual(worker_result["result"]["status"], "sync_msg_processed")
        self.assertEqual(worker_result["result"]["processed_count"], 1)
        self.assertEqual(messages[0]["incoming_text"], "老板又临下班改需求，真的离谱")
        self.assertIn("站你这边", messages[0]["reply_text"])
        self.assertEqual(seen_requests[0]["name"], "get_access_token")
        self.assertEqual(seen_requests[1]["name"], "sync_msg")
        self.assertEqual(seen_requests[1]["json"]["token"], "pull-token")
        self.assertEqual(seen_requests[1]["json"]["open_kfid"], "wkf-123")
        self.assertEqual(seen_requests[2]["name"], "get_access_token")
        self.assertEqual(seen_requests[3]["name"], "send_msg")
        self.assertEqual(seen_requests[3]["json"]["touser"], "external-owner")
        self.assertEqual(seen_requests[3]["json"]["open_kfid"], "wkf-123")
        self.assertIn("站你这边", seen_requests[3]["json"]["text"]["content"])
        self.assertEqual(worker_result["result"]["send_policy"], "real_text_send")
        self.assertEqual(worker_result["result"]["send_results"][0]["status"], "sent")
        self.assertEqual(worker_result["result"]["send_results"][0]["msgid"], "sent-sync-msg-1")
        sync_audit = [event for event in audit_events if event["event_type"] == "wecom_live_sync_msg_processed"][0]
        self.assertEqual(sync_audit["payload"]["processed_count"], 1)
        self.assertNotIn("access-token", str(sync_audit["payload"]))
        self.assertNotIn("secret", str(sync_audit["payload"]))

    def test_wecom_live_kf_msg_event_missing_sync_secret_is_acked_and_audited(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<MsgType><![CDATA[event]]></MsgType>"
            "<Event><![CDATA[kf_msg_or_event]]></Event>"
            "<Token><![CDATA[pull-token]]></Token>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(
            aes_key,
            inner_xml,
            "ww-corp",
            random_bytes=b"abcdefghijklmnop",
        )
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(store, config, query, body)
            worker_result = process_next_wecom_live_job(store, config)
            audit_events = store.list_audit_events()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(worker_result["result"]["status"], "sync_msg_deferred")
        self.assertEqual(worker_result["result"]["send_policy"], "ack_only")
        sync_audit = [event for event in audit_events if event["event_type"] == "wecom_live_sync_msg_deferred"][0]
        self.assertEqual(sync_audit["payload"]["reason"], "missing_sync_config")

    def test_wecom_live_callback_quick_ack_queues_direct_text_without_sending_inline(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<FromUserName><![CDATA[external-owner]]></FromUserName>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[老板又临下班改需求，真的离谱]]></Content>"
            "<MsgId>live-msg-async-1</MsgId>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(aes_key, inner_xml, "ww-corp", random_bytes=b"abcdefghijklmnop")
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }
        seen_requests = []

        def fake_transport(request):
            seen_requests.append(request)
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "send_msg":
                return {"errcode": 0, "errmsg": "ok", "msgid": "sent-async-1"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            response = create_wecom_live_callback_response(
                store,
                config,
                query,
                body,
                send_transport=fake_transport,
            )
            messages_before_worker = store.list_messages()
            jobs_before_worker = store.list_wecom_callback_jobs()
            audits_before_worker = store.list_audit_events()
            queued_requests = list(seen_requests)
            worker_result = process_next_wecom_live_job(store, config, send_transport=fake_transport)
            user = store.get_user_by_handle("wechat:external-owner")
            messages_after_worker = store.list_messages(user["id"])
            jobs_after_worker = store.list_wecom_callback_jobs()

        self.assertEqual(response["ack_text"], "success")
        self.assertEqual(response["status"], "queued")
        self.assertEqual(response["job_status"], "queued")
        self.assertEqual(messages_before_worker, [])
        self.assertEqual(queued_requests, [])
        self.assertEqual(len(jobs_before_worker), 1)
        self.assertEqual(jobs_before_worker[0]["status"], "queued")
        self.assertEqual(audits_before_worker[0]["event_type"], "wecom_live_callback_queued")
        self.assertEqual(worker_result["status"], "done")
        self.assertEqual(seen_requests[0]["name"], "get_access_token")
        self.assertEqual(seen_requests[1]["name"], "send_msg")
        self.assertEqual(messages_after_worker[0]["incoming_text"], "老板又临下班改需求，真的离谱")
        self.assertEqual(jobs_after_worker[0]["status"], "done")

    def test_wecom_live_duplicate_callback_is_acked_without_second_job_or_send(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        inner_xml = (
            "<xml>"
            "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
            "<FromUserName><![CDATA[external-owner]]></FromUserName>"
            "<MsgType><![CDATA[text]]></MsgType>"
            "<Content><![CDATA[今天真的有点累]]></Content>"
            "<MsgId>live-msg-duplicate</MsgId>"
            "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
            "</xml>"
        )
        encrypted = encrypt_wecom_message(aes_key, inner_xml, "ww-corp", random_bytes=b"abcdefghijklmnop")
        body = f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>"
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
        }
        seen_requests = []

        def fake_transport(request):
            seen_requests.append(request)
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "send_msg":
                return {"errcode": 0, "errmsg": "ok", "msgid": "sent-duplicate"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            first = create_wecom_live_callback_response(store, config, query, body)
            duplicate = create_wecom_live_callback_response(store, config, query, body)
            jobs = store.list_wecom_callback_jobs()
            process_next_wecom_live_job(store, config, send_transport=fake_transport)
            process_next_wecom_live_job(store, config, send_transport=fake_transport)
            user = store.get_user_by_handle("wechat:external-owner")
            messages = store.list_messages(user["id"])
            audit_events = store.list_audit_events(limit=10)

        self.assertEqual(first["status"], "queued")
        self.assertEqual(duplicate["status"], "duplicate")
        self.assertEqual(duplicate["ack_text"], "success")
        self.assertEqual(len(jobs), 1)
        self.assertEqual([request["name"] for request in seen_requests], ["get_access_token", "send_msg"])
        self.assertEqual(len(messages), 1)
        self.assertTrue(any(event["event_type"] == "wecom_live_callback_duplicate" for event in audit_events))

    def test_wecom_live_sync_worker_dedupes_synced_message_id_across_callbacks(self):
        from app.server import create_wecom_live_callback_response, process_next_wecom_live_job
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, encrypt_wecom_message, load_wecom_config_from_env

        aes_key = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG"
        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": aes_key,
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )

        def build_event(token):
            inner_xml = (
                "<xml>"
                "<ToUserName><![CDATA[ww-corp]]></ToUserName>"
                "<MsgType><![CDATA[event]]></MsgType>"
                "<Event><![CDATA[kf_msg_or_event]]></Event>"
                f"<Token><![CDATA[{token}]]></Token>"
                "<OpenKfId><![CDATA[wkf-123]]></OpenKfId>"
                "</xml>"
            )
            encrypted = encrypt_wecom_message(aes_key, inner_xml, "ww-corp", random_bytes=b"abcdefghijklmnop")
            return (
                {
                    "timestamp": "1700000000",
                    "nonce": "nonce",
                    "msg_signature": build_wecom_signature("token", "1700000000", "nonce", encrypted),
                },
                f"<xml><Encrypt><![CDATA[{encrypted}]]></Encrypt></xml>",
            )

        seen_requests = []

        def fake_transport(request):
            seen_requests.append(request)
            if request["name"] == "get_access_token":
                return {"errcode": 0, "access_token": "access-token"}
            if request["name"] == "sync_msg":
                return {
                    "errcode": 0,
                    "has_more": 0,
                    "msg_list": [
                        {
                            "msgid": "same-sync-msg",
                            "open_kfid": "wkf-123",
                            "external_userid": "external-owner",
                            "msgtype": "text",
                            "text": {"content": "老板又临下班改需求，真的离谱"},
                        }
                    ],
                }
            if request["name"] == "send_msg":
                return {"errcode": 0, "errmsg": "ok", "msgid": "sent-sync-once"}
            raise AssertionError(f"unexpected request {request}")

        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            query_one, body_one = build_event("pull-token-1")
            query_two, body_two = build_event("pull-token-2")
            create_wecom_live_callback_response(store, config, query_one, body_one)
            create_wecom_live_callback_response(store, config, query_two, body_two)
            process_next_wecom_live_job(store, config, sync_transport=fake_transport)
            process_next_wecom_live_job(store, config, sync_transport=fake_transport)
            user = store.get_user_by_handle("wechat:external-owner")
            messages = store.list_messages(user["id"])
            audit_events = store.list_audit_events(limit=20)

        self.assertEqual([request["name"] for request in seen_requests].count("sync_msg"), 2)
        self.assertEqual([request["name"] for request in seen_requests].count("send_msg"), 1)
        self.assertEqual(len(messages), 1)
        self.assertTrue(any(event["event_type"] == "wecom_live_message_duplicate" for event in audit_events))

    def test_wecom_live_normalizes_dev_plaintext_event_and_send_payload(self):
        from app.wecom_live import build_text_send_payload, normalize_live_event

        inbound = normalize_live_event(
            {
                "channel": "wecom_live",
                "external_userid": "external-owner",
                "open_kfid": "wkf-123",
                "msgtype": "text",
                "text": {"content": "老板又临下班改需求，真的离谱"},
                "msgid": "live-msg-1",
            }
        )
        payload = build_text_send_payload(inbound, "我先站你这边。")

        self.assertEqual(inbound["channel"], "wecom_live")
        self.assertEqual(inbound["external_user_id"], "external-owner")
        self.assertEqual(inbound["open_kfid"], "wkf-123")
        self.assertEqual(inbound["content"], "老板又临下班改需求，真的离谱")
        self.assertEqual(payload["touser"], "external-owner")
        self.assertEqual(payload["open_kfid"], "wkf-123")
        self.assertEqual(payload["msgtype"], "text")
        self.assertEqual(payload["text"]["content"], "我先站你这边。")

    def test_wecom_live_dev_inbound_flow_uses_companion_and_send_payload(self):
        from app.server import create_wecom_live_dev_response, handle_wecom_live_callback_validation
        from app.storage import Storage
        from app.wecom_live import build_wecom_signature, load_wecom_config_from_env

        config = load_wecom_config_from_env(
            {
                "WECOM_CORP_ID": "ww-corp",
                "WECOM_KF_SECRET": "secret",
                "WECOM_KF_TOKEN": "token",
                "WECOM_KF_ENCODING_AES_KEY": "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFG",
                "WECOM_OPEN_KFID": "wkf-123",
            }
        )
        query = {
            "timestamp": "1700000000",
            "nonce": "nonce",
            "echostr": "encrypted",
            "msg_signature": build_wecom_signature("token", "1700000000", "nonce", "encrypted"),
        }
        with tempfile.TemporaryDirectory() as tmp:
            store = Storage(Path(tmp) / "app.db")
            store.initialize()
            callback = handle_wecom_live_callback_validation(config, query)
            response = create_wecom_live_dev_response(
                store,
                {
                    "external_userid": "external-owner",
                    "open_kfid": "wkf-123",
                    "msgtype": "text",
                    "text": {"content": "老板又临下班改需求，真的离谱"},
                    "msgid": "live-msg-2",
                },
            )

        self.assertEqual(callback["status"], "base64_invalid")
        self.assertEqual(response["inbound"]["channel"], "wecom_live")
        self.assertEqual(response["outbound_payload"]["touser"], "external-owner")
        self.assertIn("站你这边", response["outbound_payload"]["text"]["content"])


if __name__ == "__main__":
    unittest.main()

import unittest
import json
import payloads

class TestPayloadsSerDe(unittest.TestCase):

    def test_serde(self):
        test_payload = payloads.P2SImageReceived("chat-id", "media-uuid", "username", "ts")
        print(test_payload)
        
        json_data = test_payload.get_bytes()
        print(json_data)

        deser_payload = json.loads(json_data, object_hook=payloads.p2s_image_received_decoder)
        print(deser_payload)

        self.assertEqual(test_payload, deser_payload)

if __name__ == '__main__':
    unittest.main()

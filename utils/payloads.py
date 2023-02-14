from dataclasses import dataclass
import json

class P2SMessageEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__

@dataclass
class P2SMessage:
    chat_id: str
    media_filename: str
    user: str
    ts: str
    message_type: str = "P2SImageReceived"

    def get_bytes(self):
        return json.dumps(self, cls=P2SMessageEncoder).encode('utf-8')

def p2s_image_received_decoder(json_dict) -> P2SMessage:
        return P2SMessage(json_dict['chat_id'], json_dict['media_filename'], json_dict['user'], json_dict['ts'], json_dict['message_type'])


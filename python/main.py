import argparse
import asyncio
import json
import os
import sys
import time

from mimi.mimi import Mimi

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--auth_config', help='path of auth config file')
    parser.add_argument('-m', '--mode', help='mode you want to use')
    parser.add_argument('-s', '--source_file', help='path of source file')
    parser.add_argument('-r', '--result_file', help='path of result file')
    args = parser.parse_args()

    with open(args.auth_config, "r", encoding="utf-8") as f:
        auth_config = json.load(f)

    mm = Mimi(auth_config)
    access_token = mm.access_token()['accessToken']

    try:
        if args.mode == 'asr':
            with open(args.source_file, 'rb') as f:
                data = f.read()
            
            result = mm.asr(access_token, data)

            with open(args.result_file, "w") as f:
                json.dump(result, f)

        elif args.mode == 'asr-ws':
            with open(args.source_file, 'rb') as f:
                data = f.read()
            
            loop = asyncio.get_event_loop()

            loop.run_until_complete(mm.asr_ws_open(access_token))
            loop.run_until_complete(mm.asr_ws_send(data))
            loop.run_until_complete(mm.asr_ws_send_break())

            result = {}
            for i in range(10):
                result = loop.run_until_complete(mm.asr_ws_recv())
                if 'status' in result and result['status'] == 'recog-finished':
                    break
                time.sleep(1)

            mm.asr_ws_close()

            with open(args.result_file, "w") as f:
                json.dump(result, f)

        elif args.mode == 'tts':
            with open(args.source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            result = mm.tts(access_token, data['text'])

            with open(args.result_file, 'wb') as f:
                f.write(result)

        elif args.mode == 'tra':
            with open(args.source_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            result = mm.tra(access_token, data['text'], data['source_lang'], data['target_lang'])

            with open(args.result_file, "w") as f:
                f.write(result)

        print('OK')
        sys.exit(0)

    except Exception as e:
        print(e)
        sys.exit(1)

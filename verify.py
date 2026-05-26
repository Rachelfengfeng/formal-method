import subprocess
import time
import os
import ast
import atexit
import socket
import portpicker
import nest_asyncio
from tqdm import tqdm
from client import Lean4Client
from datasets import Dataset
from utils import clean_up_lean


def verify_lean(codes, kimina_batch_size=20480, timeout=300, lean_port=None, max_retries=5):
    nest_asyncio.apply()

    for attempt in range(max_retries):
        server_process = None
        if lean_port is None:
            server_process, current_port = start_kimina_server()
        else:
            current_port = lean_port

        try:
            client = Lean4Client(base_url=f"http://127.0.0.1:{current_port}")

            final_results = []
            num_batches = (len(codes) + kimina_batch_size - 1) // kimina_batch_size
            for i in tqdm(range(num_batches)):
                batch = codes[i*kimina_batch_size:(i+1)*kimina_batch_size]
                requests = [
                    {"proof": clean_up_lean(code), "custom_id": str(i)}
                    for i, code in enumerate(batch)
                ]
                responses = client.verify(requests, timeout=timeout)
                assert len(responses["results"]) == len(requests)
                results = {r["custom_id"]: r for r in responses["results"]}

                for request in requests:
                    result = results[request["custom_id"]]
                    response = result["response"]
                    ret = {
                        "system_error": result["error"],
                        "_response": response,
                        "code": request["proof"],
                    }
                    if not response:
                        print("no response!", str(result)[:1000])
                        assert result["error"]
                        ret.update({
                            "errors": [],
                            "sorries": [],
                            "time": None,
                        })
                    else:
                        ret.update({
                            "errors": [message for message in response.get("messages", [])
                                        if message and message["severity"] == "error"],
                            "sorries": response.get("sorries", []),
                            "time": response["time"],
                        })
                    ret["passed"] = not ret["errors"] and not ret["system_error"]
                    ret["complete"] = ret["passed"] and not ret["sorries"]
                    final_results.append(ret)

            return final_results
        except Exception as e:
            print(f"Server connection/verification failed (attempt {attempt + 1}/{max_retries}): {e}")
            if attempt == max_retries - 1:
                raise
        finally:
            if server_process is not None:
                stop_kimina_server(server_process)


def start_kimina_server():
    port = portpicker.pick_unused_port()
    process = subprocess.Popen(
        ["python", "-m", "server"],
        cwd="kimina-lean-server", env={**os.environ, "LEANSERVER_PORT": str(port)},
    )
    sleep_s = int(os.environ.get("LEANSERVER_STARTUP_SLEEP", "3"))
    requested_max_wait_s = int(os.environ.get("LEANSERVER_STARTUP_MAX_WAIT", "30"))
    max_wait_s = max(0, requested_max_wait_s)

    initial_sleep_s = min(max(0, sleep_s), max_wait_s)
    if initial_sleep_s:
        time.sleep(initial_sleep_s)

    connected = False
    deadline = time.time() + max(0.0, max_wait_s - initial_sleep_s)
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=1):
                connected = True
                break
        except OSError:
            time.sleep(0.5)
    if not connected:
        raise RuntimeError(f"Lean server did not become reachable within {max_wait_s}s (port={port}).")

    atexit.register(process.terminate)
    return process, port


def stop_kimina_server(process):
    process.terminate()
    process.wait()


def verify(ds, output_key="formal_proof", lean_port=None):
    print(f"Running verification for {len(ds)} examples...")

    results = verify_lean(ds[output_key], lean_port=lean_port)

    cnt_complete = sum(item["complete"] for item in results)
    cnt_passed = sum(item["passed"] for item in results)
    num_examples = len(results)
    rate_complete = cnt_complete * 1. / num_examples
    rate_passed = cnt_passed * 1. / num_examples

    print(f"Complete: {cnt_complete} out of {num_examples}, rate={rate_complete}")
    print(f"Passed: {cnt_passed} out of {num_examples}, rate={rate_passed}")

    def normalize_results(example):
        example["_response"] = str(example["_response"])
        for key in ["_response", "errors", "sorries", "system_error"]:
            example[key] = str(example[key])
        return example

    results = Dataset.from_list(results).map(normalize_results, num_proc=16)

    return results


def evaluate_complexity(proof):
    if proof['complete']:
        return len(ast.literal_eval(proof["lean"]["_response"])["tactics"])
    else:
        return 1e9


def add_lean_results(ds, ret_lean):
    def add_ret_lean(example, idx):
        # pylint: disable=cell-var-from-loop
        return {
            "passed": ret_lean[idx]["passed"],
            "complete": ret_lean[idx]["complete"],
            "lean": {
                k: ret_lean[idx][k]
                for k in ["errors", "sorries", "system_error", "time", "code", "_response"]
            }
        }
    ds = ds.map(add_ret_lean, with_indices=True)
    return ds

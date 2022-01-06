import requests
import json
import argparse

BONDED_QUERY = '{\n rewardState: WasmContractsContractAddressStore(\n ContractAddress: \"terra17yap3mhph35pcwvhza38c2lkj7gzywzy05h7l0\"\n QueryMsg: \"{\\\"state\\\":{}}\"\n ) {\n Result\n Height\n }\n claimableReward: WasmContractsContractAddressStore(\n ContractAddress: \"terra17yap3mhph35pcwvhza38c2lkj7gzywzy05h7l0\"\n QueryMsg: \"{\\\"holder\\\":{\\\"address\\\":\\\"<holder_address>\\\"}}\"\n ) {\n Result\n Height\n }\n}\n'
URL = "https://mantle.terra.dev/?bond--claimable-rewards"

#[Holder Balance * (Global Index - Holder Index)] + Pending Rewards
#Found in source code of AnchorProtocol Application, still trying to figure out what this means
#https://github.com/Anchor-Protocol/anchor-web-app/blob/master/app/src/pages/bond/logics/claimableRewards.ts
def calculate_claimable_rewards(data):
    claimable_reward = json.loads(data["data"]["claimableReward"]["Result"])
    reward_state = json.loads(data["data"]["rewardState"]["Result"])

    holder_balance = int(claimable_reward["balance"])
    holder_index = float(claimable_reward["index"])
    pending_rewards = int(float(claimable_reward["pending_rewards"]))
    global_index = float(reward_state["global_index"])

    claimable_rewards = (holder_balance * (global_index - holder_index)) + pending_rewards

    return claimable_rewards

#Gets the RPC response for the Terra bonded Luna contract
def get_bonded_rewards_resp(holder_address):

    query = {
        "query": BONDED_QUERY.replace("<holder_address>", holder_address),
        "variables": {}
    }

    req = requests.post(URL, json=query)

    try:
        req.raise_for_status()
    except Exception as e:
        print(e)
        print("Something went wrong getting data from the API, please try again later")
    
    return req.json()

def parse_args():
    arg_parser = argparse.ArgumentParser(description='Query the Anchor Protocol to get your current bLuna claimable rewards')
    arg_parser.add_argument("--terra-address", type=str, help="The terra address to gather data for", required=True)
    
    return arg_parser.parse_args()

def main():
    args = parse_args()

    terra_address = args.terra_address

    resp = get_bonded_rewards_resp(terra_address)
    ubluna_claimable_rewards = calculate_claimable_rewards(resp)
    bluna_claimable_rewards = ubluna_claimable_rewards / 1000000
    
    #This doesn't produce the same result as Anchor, they seem to truncate without rounding???
    #print(format(bluna_claimable_rewards, '.3f'))
    
    #this is dumb, but do it anyway to match the Anchor display
    split = str(bluna_claimable_rewards).split(".")
    int_part = split[0]
    float_part = split[1][:3]
    print(int_part + "." + float_part, "UST")

if __name__ == "__main__":
    main()

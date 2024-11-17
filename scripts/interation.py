from brownie import Powerball, network, Contract, exceptions
from web3 import Web3
from scripts.deploy import deploy
from scripts.helpers import get_account

class PowerballGame():
    def __init__(self):
        self.startup_options = {
            1: {"name":"Deploy New Contract","action":self.startup_deploy_contract},
            2: {"name":"Get COntract from Contract Address","action":self.startup_get_contract},
        }
        self.game_options = {
            1: {"name":"Buy ticket with Powerball numbers","action":self.buy},
            2: {"name":"Draw Number for a round","action":self.draw_number},
            3: {"name":"Claim Reward if lucky","action":self.claim}
        }
        contract = self.startup()
        if not contract:
            return
        self.game_ended = False
        self.contract = contract
        self.account = get_account()
        self.game()
    def get_action_names(self, options):
        keys = options.keys()
        names = list(map(lambda x: f"{x}. {options[x]['name']}", keys))
        return names
    def startup(self):
        startup_text = """
-------------------------- Welcome to Powerball Blockchain Game -------------------------------------\n
--------------------------        Created by CodeBestia         -------------------------------------
"""
        print(startup_text)
        contract = None
        if len(Powerball) == 0:
            print("No Contract Found")
            contract = deploy()
        else:
            while True:
                print("How will you like to start the game")
                print("\n".join(self.get_action_names(self.startup_options)))
                answer = input("")
                if not answer.isnumeric():
                    print("Provide a numeric answer")
                elif  not int(answer)  in self.startup_options.keys():
                    print("Provide a answer from the valid listed options")
                else:
                    contract = self.startup_options[int(answer)]['action']()
                    if contract:
                        break
        return contract

    def startup_deploy_contract(self):
        contract = deploy()
        return contract
    def startup_get_contract(self):
        print("Enter the Contract Address of the Powerball game you want to interact with")
        address = input("")
        try:
            contract = Contract(address)
        except exceptions.ContractNotFound:
            print(f"No Contract Found at {address}")
            return None
        return contract
    def get_ticket_price(self):
        if not self.contract:
            print("Contract not found")
        price = self.contract.ticketPrice()
        eth_price = Web3.fromWei(price,"ether")
        return eth_price
    def buy(self):
        tickets = []
        print("---------- Buying Ticket --------------")
        while True:
            ticket_number = input("How many tickets will you like to buy: ")
            if not ticket_number.isnumeric():
                print("Provide a numeric choice.")
            elif int(ticket_number) < 1:
                print("Number of tickets to buy should be greater than 0")
            else:
                ticket_number = int(ticket_number)
                break
        print(f"PRICE TO PAY => {ticket_number * self.get_ticket_price()} ether")

        print("--------------------- Please read the instruction ---------------------")
        print("Enter 6 powerball number. The first 5 numbers should be less than 70 and greater than 0")
        print("The last number (powerball number) should be less than 27 and greater than 0")
        print("Enter the number in a comma-seprated format. e.g 2,23,45,65,59,11")
        for idx in range(ticket_number):
            while True:
                answer = input(f"Your numbers for ticket no. {idx + 1}: ")
                if len(answer.split(",")) != 6:
                    print("Your numbers should be comma seperated and should be 6 numbers")
                elif not all(map(lambda x: x.isnumeric(),answer.split(","))):
                    print("All choices numbers should be numeric")
                elif not all(map(lambda x: int(x) > 0,answer.split(","))):
                    print("All Chosen numbers should be greater than 0")
                elif not all(map(lambda x: int(x) < 70,answer.split(",")[:5])):
                    print("All Chosen numbers excluding the powerball number should be less than 70")
                elif not int(answer.split(",")[-1]) < 27:
                    print("The last number (the powerball number) should be less than 27")
                else:
                    answer = answer.split(",")
                    int_answers = list(map(lambda x: int(x),answer))
                    tickets.append(int_answers)
                    break
        print("Buying ticket from contract")
        try:
            tx = self.contract.buy(tickets,{"from":self.account})
            tx.wait()
            print(tx.info())
        except exceptions.VirtualMachineError:
            print("An Error Occurred while trying to buy ticket")


    def draw_number(self):
        print("---------- Drawing the lucky number for a round ----------------")
        print("Enter the round that you want to draw the lucky numbers. make sure the round has ended.")
        while True:
            answer = input("Round Number: ")
            if not answer.isnumeric():
                print("Round number must be numeric")
            elif int(answer) < 1:
                print("Round number should be greater than 0")
            else:
                answer = int(answer)
                break
        print("----------------- Drawing Numbers ----------------")
        try:
            tx = self.contract.drawNumber(answer,{"from":self.account})
            tx.wait()
        except exceptions.VirtualMachineError as err:
            print("An Error Occured when trying to draw numbers")
            print("details:", err)
            return
        print("------------------ Getting winning Numbers -----------------")
        numbers = self.contract.getWinningNumbers(answer)
        print("The Winning Numbers are")
        print(numbers)
    def claim(self):
        print("---------- Claim Reward for a round if lucky----------------")
        print("Enter the round that you want to claim the reward from. make sure the round has ended.")
        while True:
            answer = input("Round Number: ")
            if not answer.isnumeric():
                print("Round number must be numeric")
            elif int(answer) < 1:
                print("Round number should be greater than 0")
            else:
                answer = int(answer)
                break
        print("------------- Claiming -----------------")
        try:
            tx = self.contract.claim(answer,{"from":self.account})
            tx.wait()
        except exceptions.VirtualMachineError as err:
            print("An Error Occured when trying to draw numbers")
            print("details:", err)
            return
        print("Check your wallet to find out if you are lucky")
    def game(self):
        while not self.game_ended:
            print("What action will you like to perform. Enter an option number or enter 0 to quit")
            print("\n".join(self.get_action_names(self.game_options)))
            while True:
                answer = input("")
                if not answer.isnumeric():
                    print("Provide a numeric choice.")
                elif int(answer) == 0:
                    self.game_ended = True
                    break
                elif not int(answer)  in self.startup_options.keys():
                    print("Provide a choice from the provided options")
                else:
                    answer = int(answer)
                    break
            
            if self.game_ended:
                print("Ending Game connection. Thanks for playing")
                break
            self.game_options[answer]["action"]()


        

def main():
    game = PowerballGame()
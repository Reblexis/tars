import re
import argparse
import shlex
import json

from Function.Core.core_controller import CoreController
from Function.Core.command_parameters import *

RESET_COMMAND_NAME = "reset"
ROTATE_COMMAND_NAME = "rotate"
TOGGLE_COMMAND_NAME = "toggle"
SAY_COMMAND_NAME = "say"
HELP_COMMAND_NAME = "help"

DEFAULT_ARGUMENTS = {
    RESET_COMMAND_NAME: {"aspect": "all"},
    ROTATE_COMMAND_NAME: {"obj": "head", "horizontal": 0.5, "vertical": 0.5},  # Slight rotation to the right and down
    TOGGLE_COMMAND_NAME: {"obj": "camera", "state": "on"},
    SAY_COMMAND_NAME: {"text": "The text that the agent will say"},
    HELP_COMMAND_NAME: {"command": "all"}
}


class Command:
    def __init__(self, name: str, description: str, parameters: list):
        self.name = name
        self.description = description
        self.parameters = parameters

    def __str__(self):
        answer: str = f"Command: {self.name}\nDescription: {self.description}\nParameters:\n"
        for i, parameter in enumerate(self.parameters):
            answer += f"{i + 1}. {parameter}\n"
        answer += f"Example usage: {self.name} "
        for parameter in self.parameters:
            if isinstance(parameter, TextParameter):
                answer += f"--{parameter.name}='{parameter.default}' "
            else:
                answer += f"--{parameter.name}={parameter.default} "
        return answer


class ResetCommand(Command):
    def __init__(self):
        super().__init__("reset", "Resets different aspects or functionalities of the robot.",
                         [DiscreteParameter("aspect", "The aspect to reset.", ["all", "motors", "camera"],
                                            DEFAULT_ARGUMENTS[RESET_COMMAND_NAME]["aspect"])])


class RotateCommand(Command):
    def __init__(self):
        super().__init__("rotate", "Rotates the head of the robot.",
                         [ContinuousParameter("horizontal", "Horizontal angle to rotate to. Ranges from -1 (right)"
                                                            " to 1 (left).", -1, 1,
                                              DEFAULT_ARGUMENTS[ROTATE_COMMAND_NAME]["horizontal"]),
                          ContinuousParameter("vertical", "Vertical angle to rotate to. Ranges from -1 (up)"
                                                          " to 1 (down).", -1, 1,
                                              DEFAULT_ARGUMENTS[ROTATE_COMMAND_NAME]["vertical"])])


class ToggleCommand(Command):
    def __init__(self):
        super().__init__("toggle", "Changes state of a certain aspect of the robot. Toggles functionalities on or off.",
                         [DiscreteParameter("obj", "The object to change the state of.", ["camera", "microphone"],
                                            DEFAULT_ARGUMENTS[TOGGLE_COMMAND_NAME]["obj"]),
                          DiscreteParameter("state", "The state to change to.", ["on", "off"],
                                            DEFAULT_ARGUMENTS[TOGGLE_COMMAND_NAME]["state"])])


class SayCommand(Command):
    def __init__(self):
        super().__init__("say", "Makes the robot say something.", [TextParameter("text", "The text to say.",
                                                                                 DEFAULT_ARGUMENTS[SAY_COMMAND_NAME][
                                                                                     "text"])])


class HelpCommand(Command):
    def __init__(self):
        options = ["all"]
        for command_name in DEFAULT_ARGUMENTS.keys():
            options.append(command_name)
        super().__init__("help", "Gives information about a certain command and explains how to use it.",
                         [DiscreteParameter("command", "The command to get help about.", options,
                                            DEFAULT_ARGUMENTS[HELP_COMMAND_NAME][
                                                "command"])])


class CommandManager:

    def __init__(self):
        self.commands = {RESET_COMMAND_NAME: (self.reset, ResetCommand), ROTATE_COMMAND_NAME:
            (self.rotate, RotateCommand),
                         TOGGLE_COMMAND_NAME: (self.toggle, ToggleCommand), SAY_COMMAND_NAME: (self.say, SayCommand),
                         HELP_COMMAND_NAME: (self.help, HelpCommand)}
        self.core_controller = None

        self.parser = argparse.ArgumentParser(description='Process agent commands.')
        self.initialize_command_parser()

    def initialize_command_parser(self):
        subparsers = self.parser.add_subparsers(dest='command_name')

        for cmd_name, (func, cmd_class) in self.commands.items():
            sub_parser = subparsers.add_parser(cmd_name)

            for param in cmd_class().parameters:
                default_value = DEFAULT_ARGUMENTS.get(cmd_name, {}).get(param.name)

                if isinstance(param, ContinuousParameter):
                    sub_parser.add_argument(f'--{param.name}', type=float, default=default_value)
                elif isinstance(param, DiscreteParameter):
                    sub_parser.add_argument(f'--{param.name}', choices=param.options, default=default_value)
                elif isinstance(param, TextParameter):
                    sub_parser.add_argument(f'--{param.name}', type=str, default=default_value)

    def initialize_core_controller(self, core_controller: CoreController):
        self.core_controller = core_controller

    def reset(self, args: dict) -> str:
        return f"Successfully reset {args['aspect']}!"

    def rotate(self, args: dict) -> str:
        self.core_controller.physical_controller.rotate_head_to(horizontal=float(args["horizontal"]),
                                                                vertical=float(args["vertical"]))
        return f"Successfully rotated head to {args['horizontal']} horizontal and {args['vertical']} vertical!"

    def toggle(self, args: dict) -> str:
        feedback_message: str = ""
        if args["obj"] == "camera":
            if args["state"] == "on" and not self.core_controller.vision_controller.show_camera:
                self.core_controller.vision_controller.enable()
            elif args["state"] == "off" and self.core_controller.vision_controller.show_camera:
                self.core_controller.vision_controller.disable()
        elif args["obj"] == "microphone":
            if args["state"] == "on" and not self.core_controller.hearing_controller.listening:
                self.core_controller.hearing_controller.enable()
            elif args["state"] == "off" and self.core_controller.hearing_controller.listening:
                self.core_controller.hearing_controller.disable()

        return f"Successfully toggled {args['obj']} {args['state']}!"

    def say(self, args: dict) -> str:
        text = args["text"]
        self.core_controller.speech_controller.process(text)
        return "Successfully said!"

    def help(self, args: dict) -> str:
        command = args["command"]

        if command == "all":
            message = "Available commands are " + ", ".join(self.commands.keys()) + ".\n"
            message += "To get help about a certain command, type 'help --command=command_name'."
            return message

        if command in self.commands:
            return str(self.commands[command][1]())
        return "No such command found."

    def execute_command(self, command: str) -> tuple:
        split_command = shlex.split(command)
        if not split_command:
            return False, "No command found."

        command_name = split_command[0]
        arg_list = split_command[1:]
        if command_name in self.commands:
            print(f"Executing command {command_name} with args {arg_list}")
            parser = argparse.ArgumentParser(description=f"{command_name} command parser")
            for parameter in self.commands[command_name][1]().parameters:
                if isinstance(parameter, ContinuousParameter):
                    parser.add_argument(f'--{parameter.name}', type=float, default=parameter.default)
                elif isinstance(parameter, DiscreteParameter):
                    parser.add_argument(f'--{parameter.name}', choices=parameter.options, default=parameter.default)
                elif isinstance(parameter, TextParameter):
                    parser.add_argument(f'--{parameter.name}', type=str, default=parameter.default)

            try:
                parsed_args = vars(parser.parse_args(arg_list))
            except SystemExit:
                return False, "Invalid arguments."

            command_feedback: str = self.commands[command_name][0](parsed_args)
            return True, command_feedback
        else:
            return False, ("No such command found. Please type only a valid command and corresponding arguments. "
                           "Nothing else.")

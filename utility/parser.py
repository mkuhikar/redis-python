import os
import sys
import re


class Parser:

    def parse_resp(message):
        """
        Parse a RESP-formatted message and return the command and its arguments.
        """
        lines = message.split('\r\n')  # Split by the RESP delimiter

        if lines[0][0] != '*':
            raise ValueError("Invalid RESP array format")

        num_elements = int(lines[0][1:])  # Number of elements in the RESP array

        if not 'PING'in lines and num_elements < 2:
            raise ValueError("RESP message must contain at least 2 elements")

        command = None
        command2 = None
        argument1 = None
        argument2 = None
        argument3 = None
        expiry = None

        i = 1
        while i < len(lines):
            print(f"Lines {lines}")
            if lines[i].startswith('$'):  # Bulk string
                length = int(lines[i][1:])
                i += 1  # Move to the next line with the actual data

                # First bulk string is the command
                if command is None:
                    command = lines[i]
                elif argument1 is None:
                    print(f"{command} {i} value {argument1}")
                    # Second bulk string is the argument
                    argument1 = lines[i]
                elif command and argument1:
                    argument2 = lines[i]
                elif command and argument1 and argument2:
                    command2 = lines[i]
                elif command and argument1 and argument2 and command2:
                    argument3 = lines[i]
                    # break
                  # Move to the next '$' or end
                # if command and command !='SET' and argument1:
                #     break
                
            else:
                i += 1
        print(f"Command {command} argument {argument1} argument2 {argument2} command2 {command2} argument3 {argument3}")
        if command is None :
            raise ValueError("Command or argument not found in RESP message")

        return command, argument1,argument2,command2,argument3
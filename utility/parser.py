import os
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
class Parser:

    def parse_resp(message):
        """
        Parse a RESP-formatted message and return the command and its arguments.
        This function will handle any Redis command and store its associated parameters.
        """
        # Split the message by the RESP delimiter
        print("Parsing details")
        lines = message.split('\r\n')
        print(f"lines {lines}")

        # Check that the first line indicates an array with '*'
        if lines[0][0] != '*':
            raise ValueError("Invalid RESP array format")

        # Extract the number of elements in the RESP array
        num_elements = int(lines[0][1:])

        # Initialize the list to store the parsed command and arguments
        parsed_elements = []

        i = 1  # Line index
        while i < len(lines):
            if lines[i].startswith('$'):  # Handle bulk string
                length = int(lines[i][1:])  # Length of the bulk string (ignored here)
                i += 1  # Move to the next line which contains the data

                # Store the actual data (command or argument)
                if len(lines[i]) == length:  # Ensure the length matches the specified bulk string length
                    parsed_elements.append(lines[i])
                else:
                    raise ValueError("Bulk string length mismatch")

            i += 1  # Move to the next line

        # Ensure that the parsed elements match the expected number of elements
        if len(parsed_elements) != num_elements:
            raise ValueError("Number of elements does not match the RESP array size")

        # The first element is the command, and the rest are the arguments
        command = parsed_elements[0].upper()  # Redis commands are usually case-insensitive
        arguments = parsed_elements[1:]  # All other elements are arguments

        print(f"Command: {command}, Arguments: {arguments}")

        # Return the command and its arguments
        return command, arguments

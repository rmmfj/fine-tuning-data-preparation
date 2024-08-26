def remove_blank_lines(filename):
    """Removes blank lines from a text file.

    Args:
      filename: The name of the file to process.
    """

    with open(filename, "r") as f:
        lines = f.readlines()

    with open(filename, "w") as f:
        for line in lines:
            if line.strip():
                f.write(line)


def remove_duplicates(input_file, output_file):
    # Read the file and store lines in a list
    with open(input_file, "r") as file:
        lines = file.readlines()

    # Remove newline characters and duplicate entries
    unique_lines = set(line.strip() for line in lines)

    # Write unique lines to a new file
    with open(output_file, "w") as file:
        for line in unique_lines:
            file.write(f"{line}\n")


if __name__ == "__main__":
    file_path = "/Users/chenyuhan/Downloads/codingdata/processed_items.txt"
    # remove_blank_lines(filename=file_path)
    remove_duplicates(input_file=file_path, output_file=file_path)

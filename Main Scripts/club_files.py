import os
import glob

# --- Configuration ---

# 1. Set the directory where your Spark job writes its output files.
#    This should match the FILE_OUTPUT_PATH from your .env file.
SPARK_OUTPUT_DIR = "/Users/himanshu/github/DE-Project--Online-Advertisement-Platform/logs_feedback_handler/output"

# 2. Set the name and path for the final, single file.
#    Using the .jsonl extension is a good practice for newline-delimited JSON.
CONSOLIDATED_FILE_PATH = "/Users/himanshu/github/DE-Project--Online-Advertisement-Platform/consolidated_feedback.jsonl"


def consolidate_spark_files():
    """
    Finds all Spark 'part-' files in the output directory,
    appends their content to a single file, and then deletes them.
    """
    if not os.path.isdir(SPARK_OUTPUT_DIR):
        print(f"Error: Source directory not found at '{SPARK_OUTPUT_DIR}'")
        return

    # Find all the part-files created by Spark. This pattern is specific to Spark's output.
    file_pattern = os.path.join(SPARK_OUTPUT_DIR, "part-*.json")
    part_files = glob.glob(file_pattern)

    if not part_files:
        print("No new Spark output files found to consolidate.")
        return

    print(f"Found {len(part_files)} files to consolidate into '{os.path.basename(CONSOLIDATED_FILE_PATH)}'.")

    # Open the target file in 'append' mode ('a').
    # This ensures that if the file already exists, we add to it instead of overwriting it.
    with open(CONSOLIDATED_FILE_PATH, "a") as outfile:
        for filepath in sorted(part_files):  # Sorting is good practice
            try:
                with open(filepath, "r") as infile:
                    # Spark writes one JSON object per line, so we can just copy the content directly.
                    content = infile.read()
                    outfile.write(content)
                
                # After successfully writing the content, remove the original part-file.
                # This cleanup is essential to avoid processing the same file twice.
                os.remove(filepath)
                print(f"Processed and removed: {os.path.basename(filepath)}")

            except Exception as e:
                print(f"Error processing file {filepath}: {e}")

    print("Consolidation complete.")


if __name__ == "__main__":
    consolidate_spark_files()
from openai import OpenAI
import csv
import json
import time

# Set your OpenAI API key
OPENAI_API_KEY = (
    "sk-proj-AbPkTpSxp6PcDMA8C***JhA5ovwBSaeisjgezLIeH"  # Replace your key here
)

client = OpenAI(
    # This is the default and can be omitted
    api_key=OPENAI_API_KEY,
)

functions = [
    {
        "name": "extract_risks_opportunities_tasks",
        "description": """
                    Analyze the text to detect risks, opportunities, and tasks.
                """,
        "parameters": {
            "type": "object",
            "properties": {
                "risks": {
                    "type": "string",
                    "description": "Identified risks from the text. This should be a concise summary or a list of risks as a single string.",
                },
                "opportunities": {
                    "type": "string",
                    "description": "Identified opportunities from the text. This should be a concise summary or a list of opportunities as a single string.",
                },
                "tasks": {
                    "type": "string",
                    "description": "Identified tasks from the text. This should be a concise summary or a list of tasks as a single string.",
                },
            },
            "required": [
                "risks",
                "opportunities",
                "tasks",
            ],
        },
    }
]


def call_chatgpt_function(company_name):
    response = client.chat.completions.create(
        model="gpt-4-0613",
        messages=[
            {
                "role": "user",
                "content": f"""Generate information from the following text: 
                    {company_name}
                """,
            }
        ],
        functions=functions,
        function_call={"name": "extract_risks_opportunities_tasks"},
    )

    # Extracting the output
    function_response = json.loads(response.choices[0].message.function_call.arguments)

    return function_response


def regenerate_info(index, row, retry=0):
    try:
        time.sleep(2)
        if retry > 0:
            print(f'Retrying "{index}"')
        else:
            print(f'Analyzing "{index}"')

        result = call_chatgpt_function(row["text"])

        result_dict = [
            [
                row["location"],
                row["state"],
                row["text"],
                result["risks"],
                result["opportunities"],
                result["tasks"],
            ]
        ]

        return result_dict
    except Exception as e:
        time.sleep(1)
        if retry > 2:
            print(f'Failed "{index}"')
            return []
        retried = regenerate_info(index, row, retry + 1)
        return retried


def read_rows_from_csv(file_path):
    rows = []
    with open(file_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            rows.append(row)
    return rows


def write_rows_to_csv(products, file_path):
    with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        # Write the new rows
        writer.writerows(products)


def main(input_csv, output_csv):
    rows = read_rows_from_csv(input_csv)

    for index, row in enumerate(rows):
        new_row = regenerate_info(index, row)

        write_rows_to_csv(new_row, output_csv)

    print(f"Updated row saved to {output_csv}")


if __name__ == "__main__":
    input_csv = "test.csv"  # Input CSV file path
    output_csv = "test_result.csv"  # Output CSV file path
    main(input_csv, output_csv)

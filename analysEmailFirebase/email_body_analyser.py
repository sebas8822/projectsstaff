import openai
import csv
import re
from gmailApi import *

# Set up OpenAI API credentials
openai.api_key = "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"

# Context for generator
#messages = "role: system, content: You are an AI program that extract information from a email given next and fill this" \
#           " camps and anything else if is not found put null and not change following tags -> company_name: , job_description:, email_intention_description:(classified between rejection, no rejection, futher action, no related to job application)"

messages = "Role: System, Content: You are an AI system designed to extract specific information from an email and fill the following fields:"\
\
     "* company_name:"\
     "* job_description:"\
     "* email_intention_description: (classified as Rejection, Offer_Position, Further_Action, or not_related_to_job_Applciaiton (if is \"not related to job application\" mark the other fields as none))"\
\
"If any of these fields cannot be found in the email, please fill them with a null value. Please use natural language processing (NLP) techniques to analyze the email content and identify the relevant information. Finally, please return the extracted information in the above format without change anything from the specified tags and keep them lowecase (company_name:,job_description:,email_intention_description:) and lines separated by enters."


def read_csv():

    # Open the CSV file and loop through each row
    with open(r'C:\Users\sebas\Desktop\Workspace\JobSearchNinja\My_Staff\Rejection_Data_Reduced.csv') as csvfile:
        reader = csv.reader(csvfile)
        next(reader) # skip the headers
        with open(r'C:\Users\sebas\Desktop\Workspace\JobSearchNinja\My_Staff\output.csv', mode='w', newline='') as outfile:
            writer = csv.writer(outfile)
            writer.writerow(['email_body', 'response', 'company_name', 'job_description', 'email_intention']) # write the headers
            for row in reader:
                email_body = ""
                # Get the value in the first column of the row and append it to email_body
                email_body += row[0] + "\n"
                response = generate_response(messages, email_body)
                company_name, job_description, email_intention = extract_info_from_string(response)
                print("-----------------Email Body-------------------")
                print(email_body)
                print("-----------------Generated Data-------------------")
                print(response)
                print("-----------------Extracted data-------------------")
                print(company_name)  # Output: MSC Technology
                print(job_description)  # Output: Junior Software Developer
                print(email_intention)  # Output: Rejection of application
                print("-----------------New data-------------------")
                writer.writerow([email_body, response, company_name, job_description, email_intention]) # write the data to the output file

# Define function to generate response to user message
def generate_response(messages, email_body):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=messages+" "+email_body,
        temperature=0,
        max_tokens=100,
        top_p=0,
        frequency_penalty=0.0,
        presence_penalty=0.0
    )

    return response.choices[0].text

# Example usage

def extract_info_from_string(raw_string):
    company_name_match = re.search(r'company_name:\s*(.*)', raw_string)
    job_description_match = re.search(r'job_description:\s*(.*)', raw_string)
    email_intention_match = re.search(r'email_intention_description:\s*(.*)', raw_string)

    company_name = company_name_match.group(1) if company_name_match else None
    job_description = job_description_match.group(1) if job_description_match else None
    email_intention = email_intention_match.group(1) if email_intention_match else None

    return company_name, job_description, email_intention


def testing_email_body():
    text = '<div style="font-family:sans-serif;"><p>Hi Johan</p><p>Since you completed your profile on Turing 20 weeks ago, we have helped so many Android (Kotlin) developers find their dream jobs. Just last week, we filled <b>15, one of which could have been your dream job</b>.</p><p>And all of them high paying, long term remote US jobs with flexible schedules and elite team members! (Isn’t that the dream now?)</p><p>Well Johan while one ship sails away, don’t think you have lost your chance just yet.</p><p>There will be a new ship tomorrow, which you could very well be on. All you have to do for that is complete your tests, starting with the <a href="https://developers.turing.com/dashboard/turing_test?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjI3NDkzOTgsImxhbmRpbmciOnRydWUsImVtYWlsIjoicGFpc2E4ODIyQGdtYWlsLmNvbSIsInJvbGVfaWQiOjMsIm5hbWUiOiJKb2hhbiBTZWJhc3RpYW4gUmFtaXJleiBWYWxsZWpvIiwiaWF0IjoxNjc2NzY2MDg4LCJleHAiOjE2ODE5NTAwODh9.7M5gGrjS-dys-W82YFUZKUXBw3ahH47l3yHUl07EKRU&utm_source=remarketing&utm_medium=email&utm_campaign=wxp_invite&utm_content=c_text&s=wxp_invite&n=c_text">Work Experience Assessment.</a></p><p>We hope to see you on the next ship, taking your career to amazing heights — and just to be clear we are talking rocket ships that will help you soar with much better salaries and career defining projects!</p><p style="text-align:center"><a href="https://developers.turing.com/dashboard/turing_test?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1aWQiOjI3NDkzOTgsImxhbmRpbmciOnRydWUsImVtYWlsIjoicGFpc2E4ODIyQGdtYWlsLmNvbSIsInJvbGVfaWQiOjMsIm5hbWUiOiJKb2hhbiBTZWJhc3RpYW4gUmFtaXJleiBWYWxsZWpvIiwiaWF0IjoxNjc2NzY2MDg4LCJleHAiOjE2ODE5NTAwODh9.7M5gGrjS-dys-W82YFUZKUXBw3ahH47l3yHUl07EKRU&utm_source=remarketing&utm_medium=email&utm_campaign=wxp_invite&utm_content=c_text&s=wxp_invite&n=c_text" style="display:inline-block;margin-bottom:12px;margin-top:12px;padding:10px;text-align:center;text-decoration:none;font-weight:bold;letter-spacing:0.72px;border:0;background-color:#4285f4;color:white;border-radius:4px" target="_blank">Take Work Experience Assessment Now</a></p><br><p>All the best,<br>Turing Career Team</p></div>"'
    text_clened = clean_body(text)
    print(text_clened)

#testing_email_body()
read_csv()


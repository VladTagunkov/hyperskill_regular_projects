# Write your code here >>>
import math
import sys

from huggingface_hub import InferenceClient

# Read HF token from .env file
with open('.env', 'r') as fp:
    HF_API_KEY = fp.read().strip()

 # Request motivation from HF
def hf_requester(subjects_,completeness_):
    client = InferenceClient(token=HF_API_KEY)
    prompt = """
            I have to prepare for my {subjects} exams. I've completed {completeness:.2f}% of my curriculum. My motivation should be:
            """.format(
        subjects=','.join(subjects_.keys()),
        completeness=completeness_
    )

    return client.text_generation(
        prompt=prompt,
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        temperature=0.01,
        max_new_tokens=50,
        seed=42,
        return_full_text=True,
    )

#Completeness calculations
def compl_calculator(time_spent_in_,total_time_):
    time_spent = int(time_spent_in_)
    completeness = round((time_spent / total_time_) * 100, 2)
    if completeness > 100:
        completeness = 100.00
    return completeness

# Total time calculator
def total_time_calculator(subjects_):
    total_time = sum(subjects_.values())
    lesson_chunks = int(total_time / 45)
    total_time_break = total_time + lesson_chunks * 15
    return total_time,total_time_break

#print subject and time from dict
def subj_time_printer(subjects_):
    for key, value in subjects_.items():
        print(f"{key}: {value} minutes")

def subj_time_dict_maker():
    while True:
        subj = input("Enter subject name:")
        if subj != "":
            try:
                minutes = int(input(f"Enter time allocated for {subj}: "))
                if minutes >= 0:
                    subjects[subj] = minutes
                else:
                    minutes = input(f"Enter time allocated for {subj}: ")
                    subjects[subj] = minutes
            except:
                minutes = input(f"Enter time allocated for {subj}: ")
                subjects[subj] = minutes
        else:
            break


subjects = {}

subj_time_dict_maker()

if len(list(subjects.keys())) != 0:
    print("Your study plan:")
    subj_time_printer(subjects)
    total_time, total_time_break = total_time_calculator(subjects)

    print(f"Total study time: {total_time} minutes")
    print(f"Total time including breaks: {total_time_break} minutes")

    time_spent_in = input("Enter time spent studying:")

    if time_spent_in != "":
        completeness = compl_calculator(time_spent_in, total_time)

        print(f"You have completed {completeness:.2f}% of your planned study time.")
        response = hf_requester(subjects,completeness)
        print(response)



#if __name__ == '__main__':
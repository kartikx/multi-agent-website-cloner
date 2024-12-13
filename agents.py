from openai_client import generate_html_code, diff_image
import webbrowser
import pyautogui
from autogen import SwarmResult
from autogen import SwarmAgent, SwarmResult, UserProxyAgent, initiate_swarm_chat, AFTER_WORK, AfterWorkOption, ON_CONDITION
from utils import llm_config

from autogen import SwarmResult
import pyautogui
import webbrowser
from openai_client import generate_html_code, diff_image


def take_screenshot(url: str, context_variables: dict) -> str:
    webbrowser.get('firefox').open(url, new=0)
    pyautogui.sleep(2)
    screenshot = pyautogui.screenshot()
    target_file_location = "target.png"
    screenshot.save(target_file_location)
    context_variables["target_file_location"] = target_file_location
    return SwarmResult(values="Done taking a screenshot. Use this to create a website.", context_variables=context_variables, agent=coder_agent)


def write_html_code(context_variables: dict) -> str:
    print("Writing HTML Code")
    html_code = generate_html_code(context_variables["target_file_location"],
                                   context_variables["attempt_code"],
                                   context_variables["feedback"])

    context_variables["attempt_code"] = html_code

    # strip block quotes
    html_code = html_code[7:]
    html_code = html_code[:-3]

    with open("website.html", "w") as f:
        f.write(html_code)

    context_variables["html_file_location"] = "website.html"
    context_variables["num_tries"] = context_variables.get("num_tries", 0) + 1

    return SwarmResult(values="Wrote HTML code. This should be tested by tester.", context_variables=context_variables, agent=tester_agent)


def test_html_code(context_variables: dict) -> str:
    print("Testing HTML Code")
    html_file_name = context_variables.get("html_file_location")
    if not html_file_name:
        return SwarmResult(values="No HTML file location found.", context_variables=context_variables)

    # open the file in firefox
    # i could reuse a function here.
    webbrowser.get('firefox').open(f'file:///Users/kartik/Code/ai-agents/website-clone-assistant/{html_file_name}',
                                   new=0)

    pyautogui.sleep(2)
    screenshot = pyautogui.screenshot()
    try_file_location = "try.png"
    screenshot.save(try_file_location)

    context_variables["try_file_location"] = try_file_location

    feedback = diff_image(
        context_variables["target_file_location"], try_file_location)

    context_variables["feedback"] = feedback

    return SwarmResult(values="Tested HTML code, website should be re-written by coder.", context_variables=context_variables, agent=coder_agent)


"""
Define the Agents.
"""
screenshot_agent = SwarmAgent(
    name="screenshotter",
    system_message="""You are a helpful assistant.
    You can use the take_screenshot function to take a screenshot of a webpage.
    Pass in the name of the webpage as an argument to the function.
    After taking a screenshot, pass it to the coder agent.
    """,
    functions=[take_screenshot],
    llm_config=llm_config,
)

coder_agent = SwarmAgent(name="coder",
                         system_message="""You are a coding assistant.
    You have the ability to write HTML code to a file.
    Always use the function write_html_code to write HTML code to a file.""",
                         functions=[write_html_code],
                         llm_config=llm_config)

tester_agent = SwarmAgent(name="tester",
                          system_message="""You are the tester.
    You have access to a function test_html_code to test HTML code.""",
                          functions=[test_html_code],
                          llm_config=llm_config)

user_agent = UserProxyAgent(name="user",
                            system_message="You are the user. You can interact with the agents to get the task done.",
                            human_input_mode="NEVER",
                            code_execution_config=False)

"""
Define transitions
"""
screenshot_agent.register_hand_off(
    hand_to=[
        ON_CONDITION(
            coder_agent, "After taking a screenshot, transfer to coder_agent.")
    ])

coder_agent.register_hand_off(
    hand_to=[
        ON_CONDITION(
            tester_agent, "After writing HTML code, transfer to tester_agent.")
    ])

tester_agent.register_hand_off(
    hand_to=[
        ON_CONDITION(
            coder_agent, "After testing HTML code, transfer back to coder_agent."),
    ])

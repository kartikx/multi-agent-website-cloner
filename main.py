from autogen import initiate_swarm_chat, AFTER_WORK, AfterWorkOption
from agents import screenshot_agent, coder_agent, tester_agent, user_agent
from utils import context_variables


if __name__ == "__main__":
    chat_result, context_variables, last_speaker = initiate_swarm_chat(
        initial_agent=screenshot_agent,
        agents=[
            screenshot_agent, coder_agent, tester_agent],
        user_agent=user_agent,
        messages=[
            "Take a screenshot of https://ag2ai.github.io/ag2/docs/tutorial/introduction/ and save it as target.png",],
        context_variables=context_variables,
        after_work=AFTER_WORK(
            AfterWorkOption.TERMINATE),
        max_rounds=12)

    print(chat_result)

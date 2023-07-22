import os
import logging
from dotenv import load_dotenv
import openai

load_dotenv()

# Get the API key from the environment variables
API_KEY = os.getenv("OPENAI_API_KEY")

# Set the API key for OpenAI
openai.api_key = API_KEY

# Define the GPT-3.5 model ID
model_id = "gpt-3.5-turbo-16k"


# Configure logging to output relevant information during execution
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_insights_from_llm(content: str, data_dictionary: dict, insights: str):
    """
    Extract insights from the given HTML code using GPT-3.5 Language Model.

    Args:
        content (str): The HTML code from which insights are to be extracted.
        data_dictionary (dict): A dictionary that serves as a schema for the data in the HTML code.
        insights (str): The specific insights to be extracted from the HTML code.

    Returns:
        str: Extracted insights in the form of a JSON array of objects.
    """
    # Log the received data and insights for debugging purposes
    logging.info("Received data_dictionary: {0}".format(data_dictionary))
    logging.info("Received insights: {0}".format(insights))

    # Define the necessary components for the conversation with GPT-3.5
    prefix_message = "You are a Transform Service powered by GPT-3.5 LLM, designed to extract insights from HTML code. Your responses should be arrays of JSON objects.\n"
    system_instructions = "As a Transform Service, please do not explain how you do your tasks and do not exchange pleasantries. You are not allow to responde with executable code. Focus only on extracting insights from the given HTML code.\n"
    user_instructions = f"Using the following data_dictionary({data_dictionary}) as a schema, extract {insights} from the given HTML code and respond as an array of JSON objects. DO NOT WRITE EXECUTABLE CODE"

    conversation = []

    # Construct the prompt for the GPT-3.5 conversation
    prompt = f"{prefix_message}{system_instructions}{user_instructions}\n"
    conversation.append(
        {
            "role": "system",
            "content": f"{prompt}",
        }
    )
    conversation.append(
        {
            "role": "user",
            "content": f"data_dictionary = {data_dictionary}\n insights = {insights}\n HTML = '''{content}'''\n",
        }
    )

    # Log that the request is being sent to the OpenAI API
    logging.info("Sending request to OpenAI API...")

    # Call GPT-3.5 API with the constructed conversation and get the response
    response = openai.ChatCompletion.create(model=model_id, messages=conversation)

    # Retrieve the API usage information from the response
    api_usage = response["usage"]
    logging.info("Total tokens consumed: {0}".format(api_usage["total_tokens"]))

    # Log the OpenAI API response content for debugging purposes
    logging.info("OpenAI API Response: {0}".format(response.choices[0].message.content))

    # Return the GPT-3.5 response content with single quotes replaced by double quotes
    return response.choices[0].message.content.replace("'", '"')


if __name__ == "__main__":
    # Test HTML content
    TEST_SITE = '<html>\n\n<body>\n<div class="header">\n<div class="container">\n<h1>NeverSSL</h1>\n</div>\n</div>\n<div class="content">\n<div class="container">\n<h2>What?</h2>\n<p>This website is for when you try to open Facebook, Google, Amazon, etc\n\ton a wifi network, and nothing happens. Type "http://neverssl.com"\n\tinto your browser s url bar, and you ll be able to log on.</p>\n<h2>How?</h2>\n<p>neverssl.com will never use SSL (also known as TLS). No\n\tencryption, no strong authentication, no <a href="https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security">HSTS</a>,\n\tno HTTP/2.0, just plain old unencrypted HTTP and forever stuck in the dark\n\tages of internet security.</p>\n<h2>Why?</h2>\n<p>Normally, that s a bad idea. You should always use SSL and secure\n\tencryption when possible. In fact, it s such a bad idea that most websites\n\tare now using https by default.</p>\n<p>And that s great, but it also means that if you re relying on\n\tpoorly-behaved wifi networks, it can be hard to get online.  Secure\n\tbrowsers and websites using https make it impossible for those wifi\n\tnetworks to send you to a login or payment page. Basically, those networks\n\tcan t tap into your connection just like attackers can t. Modern browsers\n\tare so good that they can remember when a website supports encryption and\n\teven if you type in the website name, they ll use https.</p>\n<p>And if the network never redirects you to this page, well as you can\n\tsee, you re not missing much.</p>\n<a href="https://twitter.com/neverssl">Follow @neverssl</a>\n</div>\n</div>\n</body>\n</html>\n'

    # Test data dictionary and insights
    data_dictionary = {
        "href": "url",
        "timestamp": "current time",
        "domain_name": "domain identifier in the url",
    }
    insights = "links"

    # Call the function and print the result
    print(get_insights_from_llm(TEST_SITE, data_dictionary, insights))

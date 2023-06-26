import os
import logging
from dotenv import load_dotenv
import openai

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = API_KEY

model_id = "gpt-3.5-turbo-16k"

prefix_message = "You are a transform service in an ETL pipeline. Do not explain how you do your tasks, do not exchange pleasantries. For any task provided, you are not a chatbot, you are a transform service. The transform service you currently are only responds in arrays of JSON objects."

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def get_insights_from_llm(content: str, data_dictionary, insights: str):
    conversation = []

    prompt = f"Using the following data_dictionary({data_dictionary}) as a schema, extract {insights} from the following HTML code as JSON objects in your response."
    conversation.append(
        {
            "role": "system",
            "content": f"{prefix_message}{prompt}\n{content}",
        }
    )

    logging.info("Sending request to OpenAI API...")
    response = openai.ChatCompletion.create(model=model_id, messages=conversation)
    api_usage = response["usage"]
    logging.info("Total tokens consumed: {0}".format(api_usage["total_tokens"]))
    logging.info("OpenAI API Response: {0}".format(response.choices[0].message.content))

    return response.choices[0].message.content.replace("'", '"')


if __name__ == "__main__":
    TEST_SITE = '<html>\n\n<body>\n<div class="header">\n<div class="container">\n<h1>NeverSSL</h1>\n</div>\n</div>\n<div class="content">\n<div class="container">\n<h2>What?</h2>\n<p>This website is for when you try to open Facebook, Google, Amazon, etc\n\ton a wifi network, and nothing happens. Type "http://neverssl.com"\n\tinto your browser s url bar, and you ll be able to log on.</p>\n<h2>How?</h2>\n<p>neverssl.com will never use SSL (also known as TLS). No\n\tencryption, no strong authentication, no <a href="https://en.wikipedia.org/wiki/HTTP_Strict_Transport_Security">HSTS</a>,\n\tno HTTP/2.0, just plain old unencrypted HTTP and forever stuck in the dark\n\tages of internet security.</p>\n<h2>Why?</h2>\n<p>Normally, that s a bad idea. You should always use SSL and secure\n\tencryption when possible. In fact, it s such a bad idea that most websites\n\tare now using https by default.</p>\n<p>And that s great, but it also means that if you re relying on\n\tpoorly-behaved wifi networks, it can be hard to get online.  Secure\n\tbrowsers and websites using https make it impossible for those wifi\n\tnetworks to send you to a login or payment page. Basically, those networks\n\tcan t tap into your connection just like attackers can t. Modern browsers\n\tare so good that they can remember when a website supports encryption and\n\teven if you type in the website name, they ll use https.</p>\n<p>And if the network never redirects you to this page, well as you can\n\tsee, you re not missing much.</p>\n<a href="https://twitter.com/neverssl">Follow @neverssl</a>\n</div>\n</div>\n</body>\n</html>\n'

    data_dictionary = {
        "href": "url",
        "timestamp": "current time",
        "domain_name": "domain identifier in the url",
    }
    insights = "links"

    print(get_insights_from_llm(TEST_SITE, data_dictionary, insights))

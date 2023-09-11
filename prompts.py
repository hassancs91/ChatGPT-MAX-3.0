blog_bullet_summary_prompt = """\
In the following input, I am going to give you a text you should summarize 
for me a bullet points format.
I will give you a maximum and a minimum amount of bullet points
you should use for the summary.
I am also going to give you the text itself after that.
The language of the text you get should define in which language you write the summary.
For Example, if the text is German the summary should be in German too.
This goes for every language.While writing the summary 
I want you to remember the following information: When it comes to writing content,
two factors are crucial, "perplexity" and "burstiness."
Perplexity measures the complexity of text. Separately,
burstiness compares the variations of sentences.
Humans tend to write with great burstiness, for example,
with some longer or complex sentences alongside shorter sentences.
AI sentences tend to be more uniform. Therefore,
when writing the following content I am going to ask you to create,
I need it to have a good amount of perplexity and burstiness.
Keep that information in mind while writing.
Maximum: [{MaxPoints}], Minimum[{MinPoints}], Text: {InputText} """


rewrite_prompt = """Your task is to enhance a given text by amplifying its originality,
removing any elements of plagiarism, and improving its readability
to make it appear as if it was written by a human. While doing so,
it is crucial to preserve the main idea and objective of the text.
The text you need to refine is provided below: {text}"""


google_search_prompt = "I will provide you with the summaries of multiple articles, extract the main points, and create a small research paragraph in 7-10 senteces. input: {input}"

import json
from managers.llm_manager import LLMManager
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field

llm_manager = LLMManager()
parser = StrOutputParser()
llm = llm_manager._get_azure_openai_llm()

promtp = prompt = PromptTemplate().from_template("""
Translate the following text from {input_language} into {output_language}, with the following requirements:
① Ensure accuracy first
② Secondly, it must conform to the described context of the given text
③ Maintain a balance between literal translation and paraphrasing
④ For any slang that exists, provide an explanation at the end of the translation
⑤ Output the results in accordance with certain formats
  1. Translation of the original text
  2. Paraphrased parts (list the original input-language parts without translating them into output-language, explain the paraphrased translation, and indicate whether it conforms to Chinese expression habits)
    •
    •
    •
 3. Existence of slang and fixed expressions
    •
    •
    •
⑥ The following is the paragraph to be translated:
{text}
""")


chain = prompt | llm | parser
js = chain.invoke(input={"input_language": "English", "output_language": "Hebrew", "text": """6 RELATED WORK
6.1 Code Summarization
Deep learning models have advanced the state-of-the-art in SE
tasks such as code summarization. The LSTM model for code summarization was first introduced by Iyer et al. [33]. Pre-trained
transformer-based [62] models such as CodeBERT [21], PLBART [2],
and CodeT5 [64] have been extensively used on the CodeXGLUE [47]
code summarization dataset, resulting in significant improvements.
However, there is a caveat to using pre-trained language models: although these models perform well, extensive fine-tuning is required,
which can be data-hungry & time-consuming. Additionally, separate models had to be trained for different languages, increasing
training costs. To reduce the number of models required, multilingual fine-tuning has been suggested, to maintain or improve
performance while reducing the number of models to one [4]. However, this approach did not reduce the training time or the need for
labeled data.
LLMs, or large language models, are much larger than these pretrained models, and are trained on much bigger datasets with a simple training objective — auto-regressive next-token prediction [12].
These models perform surprisingly well on tasks, even without finetuning. Just prompting the model with different questions, while
providing a few problem-solution exemplars, is sufficient. Few-shot
learning has already been applied to code summarization, and has
been found to be beneficial [3].
Automatic Semantic Augmentation of Language Model Prompts
(for Code Summarization) ICSE ’24, April 14–20, 2024, Lisbon, Portugal
6.2 Other Datasets
There are several datasets available for code summarization, in addition to CodeXGLUE [47]. TL-CodeSum [30] is a relatively smaller
dataset, with around 87K samples, but it does include duplicates,
which may result in high performance estimates that may not generalize. Funcom [41] is a dedicated dataset with 2.1 million Java
functions, but contains duplicates. We chose CodeXGLUE (derived
from CodeSearchNet) because it is a diverse, multilingual dataset
that presents a challenge for models. Even well-trained models
like CodeBERT struggle on this benchmark; its performance is
particularly poor on languages with fewer training samples.
There has been a lot of work on code summarization, ranging
from template matching to few-shot learning. These models use
different representations and sources of information to perform
well in code summarization. Comparing or discussing all of these
models is beyond the scope of this work. We note, however, that our
numbers represent a new high-point on the widely used CodeXGlue
benchmark for code summarization and code-completion; we refer
the reader to https://microsoft.github.io/CodeXGLUE/ for a quick
look at the leader-board. Our samples are smaller (N=1000), but the
estimates, and estimated improvements, are statistically robust (See
the sample size discussion in Section 7).
6.3 LLMs in Software Engineering
Although LLMs are not yet so widely used for code summarization,
they are extensively used for code generation [14, 49, 67] and program repair [5, 18, 35, 36]. Models like Codex aim to reduce the
burden on developers by automatically generating code or completing lines. Several models such as Polycoder [67] and Codegen [49]
perform reasonably well, and due to their few-shot learning or
prompting, they can be applied to a wide set of problems. However,
Code-davinci-002 model generally performs well than those models
and allows us to fit our augmented prompts into a bigger window.
Jain et al. proposed supplementing LLM operation with subsequent processing steps based on program analysis and synthesis
techniques to improve performance in program snippet generation [34]. Bareiß et al. showed the effectiveness of few-shot learning
in code mutation, test oracle generation from natural language documentation, and test case generation tasks [10]. CODAMOSA [42],
an LLM-based approach, conducts search-based software testing
until its coverage improvements stall, then asks the LLM to provide
example test cases for functions that are not covered. By using these
examples, CODAMOSA helps redirect search-based software testing to more useful areas of the search space. Jiang et al. evaluated
the effectiveness of LLMs for the program repair problem [35].
Retrieving and appending a set of training samples has been
found to be beneficial for multiple semantic parsing tasks in NLP,
even without using LLM [68]. One limitation of this approach is that
performance can be constrained by the availability of similar examples. Nashid et al. used a similar approach and gained improved
performance in code repair and assertion generation with the help
of LLM [48]. However, none of the above works has attempted to
automatically semantically augment the prompt. Note that it is still
too early to comment on the full capabilities of these large language
models. Our findings so far suggest that augmenting the exemplars
in the prompt with semantic hints helps on the code summarization
and code completion tasks; judging the value of A𝑆𝐴𝑃 in other
tasks is left for future work.

"""})

print(js)

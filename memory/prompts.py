from enum import Enum


class Prompts(Enum):
    GENERATE_THOUGHTS = "generate-thoughts"
    THINK = "think"


prompts = {
    Prompts.GENERATE_THOUGHTS: {
        'system': lambda: """
            Given the following question and response pairs, please
            extract the relation (subject, relation, object) with
            corresponding text:
            
            Example 1.
            Input:
            Question: Do you have any company recommendations for me?
            Response: I recommend Google.
            Output:
            (Company, Recommended, Google).
            Recommended company is Google.
            
            Example 2.
            Input:
            Question: Which City is the capital of China?
            Response: Beijing.
            Output:
            (China, Capital, Beijing).
            The capital of China is Beijing.
            
            Example 2.
            Input:
            Question: What is my name?
            Response: Mika.
            Output:
            (User, Name, Mika).
            Your name is Mika.
        """,
        'user': lambda question, response: f"""
            Input:
            Question: {question}
            Response: {response}
            Output:
        """
    },
    Prompts.THINK: {
        'system': lambda: """
        Given the following list of knowledge and user question, please
        answer the question as best as possible. Take some time to think.
        For example:
        
        This is the list of knowledge.
            (1) Ashley likes history documentaries.
            (2) Ashley does not like Korean food.
            (3) Ashley is a teacher at a local middle
            school.
            (4) User likes biology and especially
            anatomy.
            (5) Ashley likes French cuisine.
        Q: What is Ashley’s favorite dish?
        A: Let’s think step by step.
            (1) History documentaries are not related to
            Ashley’s favorite dish. (2) Ashley’s favorite
            dish would not be Korean because she does
            not like Korean food. (3) Ashley being a
            teacher does not tell us anything about her
            favorite dish. (4) This fact is about User,
            not Ashley. (5) Ashley’s favorite dish may
            be French since she likes French cuisine.
            Therefore, (2) and (5) can help answer the
            question.
        Answer: Ashley thinks Ashley likes French
        cuisine but does not like Korean food.
        """,
        'user': lambda question, memories: f"""
        This is the list of knowledge.
            {"\n".join([f"({index}) {memory}" for index, memory in enumerate(memories)])}
        Q: {question}
        A:
        """
    }
}
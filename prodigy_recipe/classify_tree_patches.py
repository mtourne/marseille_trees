import prodigy
from prodigy.components.loaders import JSONL

OPTIONS = [
    {"id": 0, "text": "GOOD TREE"},
    {"id": 1, "text": "NOT A TREE"},
    {"id": 2, "text": "BOX trop grande ou trop petite"},
]

@prodigy.recipe("classify-trees")
def classify_trees(dataset, source):
    def get_stream():
        # Load the directory of images and add options to each task
        stream = JSONL(source)
        for eg in stream:
            eg["options"] = OPTIONS
            yield eg

    return {
        "dataset": dataset,
        "stream": get_stream(),
        "view_id": "choice",
        "config": {
            "choice_style": "single",  # or "multiple"
            # Automatically accept and submit the answer if an option is
            # selected (only available for single-choice tasks)
            "choice_auto_accept": True
        }
    }

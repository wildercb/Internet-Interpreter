# Code to train an efficent distillBert model for binary classification of text. 
# Recommended to run in google collab will roughly take 1 hour for 5000 title training set and 3 epochs
from google.colab import files
import pandas as pd
import io
# !pip install datasets transformers huggingface_hub
# !apt-get install git-lfs
from datasets import load_dataset
from datasets import Dataset
uploadedTrain = files.upload()
uploadedTest = files.upload()

import torch
torch.cuda.is_available()

# !pip install datasets transformers huggingface_hub
# !apt-get install git-lf

dfTrain = pd.read_csv(io.BytesIO(uploadedTrain['titlesForBertJrTrain.csv']))
dfTest = pd.read_csv(io.BytesIO(uploadedTest['titlesForBertJrTest.csv']))


# Convert the Pandas DataFrame to a Hugging Face Dataset
hf_dataset = Dataset.from_pandas(dfTrain)
hf_datasetTest = Dataset.from_pandas(dfTest)

hf_dataset = hf_dataset.rename_column("title", "text")

# Define test and train datasets
small_train_dataset = hf_dataset.shuffle(seed=42).select([i for i in range(5000)])
small_test_dataset = hf_dataset.shuffle(seed=42).select([i for i in range(300)])


print(small_train_dataset)
print(small_test_dataset)

# Preprocess data with distillbert
from transformers import AutoTokenizer
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")


def preprocess_function(examples):
   return tokenizer(examples["text"], truncation=True)
 
tokenized_train = small_train_dataset.map(preprocess_function, batched=True)
tokenized_test = small_test_dataset.map(preprocess_function, batched=True)

# Convert to pytorch samples and tokenize
from transformers import DataCollatorWithPadding
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

# Now data is processed and can be used to train model 

from transformers import AutoModelForSequenceClassification
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)

import numpy as np
from datasets import load_metric
 
# Define our metrics for evaluation
def compute_metrics(eval_pred):
   load_accuracy = load_metric("accuracy")
   load_f1 = load_metric("f1")
  
   logits, labels = eval_pred
   predictions = np.argmax(logits, axis=-1)
   accuracy = load_accuracy.compute(predictions=predictions, references=labels)["accuracy"]
   f1 = load_f1.compute(predictions=predictions, references=labels)["f1"]
   return {"accuracy": accuracy, "f1": f1}

# Import your hugging face account and use token to actually deploy model 
from huggingface_hub import notebook_login
notebook_login()

from transformers import TrainingArguments, Trainer
 
repo_name = "bert-s-jr"
 
# Define our training arguments at 2 epochs was roughly 94% @ 5000 titles
# At 3000 titles was 92% training accuracy after 2 epochs
training_args = TrainingArguments(
   output_dir=repo_name,
   learning_rate=2e-5,
   per_device_train_batch_size=16,
   per_device_eval_batch_size=16,
   num_train_epochs=3,
   weight_decay=0.01,
   save_strategy="epoch",
   push_to_hub=True,
)
 
trainer = Trainer(
   model=model,
   args=training_args,
   train_dataset=tokenized_train,
   eval_dataset=tokenized_test,
   tokenizer=tokenizer,
   data_collator=data_collator,
   compute_metrics=compute_metrics,
)

trainer.train()

trainer.evaluate()


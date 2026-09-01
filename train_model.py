import pandas as pd
import numpy as np
import re
import pickle
from collections import Counter
from math import log


# ==========================================
# 1. LOAD DATASET
# ==========================================

print("Loading dataset...")

data = pd.read_csv("dataset/mail_data.csv")

print("Dataset loaded successfully!")
print("Dataset shape:", data.shape)

data = data[["Category", "Message"]].dropna()

data["Category"] = data["Category"].map({
    "ham": 0,
    "spam": 1
})

print("\nClass distribution:")
print(data["Category"].value_counts())


# ==========================================
# 2. TEXT CLEANING
# ==========================================

def clean_text(text):
    text = str(text).lower()

    text = re.sub(
        r"http\S+|www\S+|https\S+",
        " URL ",
        text
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


data["Message"] = data["Message"].apply(clean_text)


# ==========================================
# 3. TRAIN / TEST SPLIT
# ==========================================

np.random.seed(42)

spam_data = data[
    data["Category"] == 1
].copy()

ham_data = data[
    data["Category"] == 0
].copy()


spam_data = spam_data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

ham_data = ham_data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


train_data = pd.concat([
    spam_data.iloc[
        :int(len(spam_data) * 0.8)
    ],
    ham_data.iloc[
        :int(len(ham_data) * 0.8)
    ]
])


test_data = pd.concat([
    spam_data.iloc[
        int(len(spam_data) * 0.8):
    ],
    ham_data.iloc[
        int(len(ham_data) * 0.8):
    ]
])


train_data = train_data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)

test_data = test_data.sample(
    frac=1,
    random_state=42
).reset_index(drop=True)


print("\nTraining samples:", len(train_data))
print("Testing samples:", len(test_data))


# ==========================================
# 4. BUILD VOCABULARY
# ==========================================

print("\nBuilding vocabulary...")

word_counts = Counter()

for message in train_data["Message"]:
    words = set(message.split())

    for word in words:
        if len(word) >= 2:
            word_counts[word] += 1


vocabulary = {}

for index, item in enumerate(
    word_counts.most_common(5000)
):
    word = item[0]
    vocabulary[word] = index


print("Vocabulary size:", len(vocabulary))


# ==========================================
# 5. CALCULATE IDF
# ==========================================

print("\nCalculating TF-IDF values...")

document_count = len(train_data)

document_frequency = Counter()


for message in train_data["Message"]:

    words = set(message.split())

    for word in words:

        if word in vocabulary:
            document_frequency[word] += 1


idf = {}

for word in vocabulary:

    df = document_frequency[word]

    idf[word] = (
        log(
            (document_count + 1)
            /
            (df + 1)
        )
        + 1
    )


# ==========================================
# 6. CREATE TF-IDF FEATURES
# ==========================================

def create_features(messages):

    features = np.zeros(
        (
            len(messages),
            len(vocabulary)
        ),
        dtype=np.float32
    )

    for row, message in enumerate(messages):

        words = message.split()

        frequencies = Counter(words)

        total_words = len(words)

        if total_words == 0:
            continue

        for word, count in frequencies.items():

            if word in vocabulary:

                index = vocabulary[word]

                tf = count / total_words

                features[row, index] = (
                    tf * idf[word]
                )

    return features


X_train = create_features(
    train_data["Message"].tolist()
)

X_test = create_features(
    test_data["Message"].tolist()
)

y_train = train_data["Category"].values
y_test = test_data["Category"].values


print("Feature matrix created!")

print(
    "Training feature shape:",
    X_train.shape
)

print(
    "Testing feature shape:",
    X_test.shape
)


# ==========================================
# 7. TRAIN NAIVE BAYES MODEL
# ==========================================

print("\nTraining spam detection model...")


spam_features = X_train[
    y_train == 1
]

ham_features = X_train[
    y_train == 0
]


spam_count = len(spam_features)
ham_count = len(ham_features)

total_count = spam_count + ham_count


# Class probabilities

spam_prior = (
    spam_count / total_count
)

ham_prior = (
    ham_count / total_count
)


# Laplace smoothing

alpha = 1.0


# Spam word probabilities

spam_word_probability = (
    spam_features.sum(axis=0)
    + alpha
)

spam_word_probability = (
    spam_word_probability
    /
    spam_word_probability.sum()
)


# Ham word probabilities

ham_word_probability = (
    ham_features.sum(axis=0)
    + alpha
)

ham_word_probability = (
    ham_word_probability
    /
    ham_word_probability.sum()
)


# Log probabilities

log_spam_prior = log(spam_prior)
log_ham_prior = log(ham_prior)

log_spam_word_probability = np.log(
    spam_word_probability
)

log_ham_word_probability = np.log(
    ham_word_probability
)


print("Model training completed!")


# ==========================================
# 8. PREDICTION
# ==========================================

def predict_features(X):

    spam_scores = (
        X @ log_spam_word_probability
        + log_spam_prior
    )

    ham_scores = (
        X @ log_ham_word_probability
        + log_ham_prior
    )

    predictions = (
        spam_scores > ham_scores
    ).astype(int)

    return predictions


# ==========================================
# 9. MODEL EVALUATION
# ==========================================

y_pred = predict_features(X_test)

accuracy = np.mean(
    y_pred == y_test
)


print("\n==========================================")
print("MODEL PERFORMANCE")
print("==========================================")

print(
    f"\nAccuracy: {accuracy * 100:.2f}%"
)


# Confusion matrix

true_negative = np.sum(
    (y_test == 0) &
    (y_pred == 0)
)

false_positive = np.sum(
    (y_test == 0) &
    (y_pred == 1)
)

false_negative = np.sum(
    (y_test == 1) &
    (y_pred == 0)
)

true_positive = np.sum(
    (y_test == 1) &
    (y_pred == 1)
)


print("\nConfusion Matrix:")

print(
    f"[[{true_negative} {false_positive}]"
)

print(
    f" [{false_negative} {true_positive}]]"
)


# Precision

precision = (
    true_positive /
    (true_positive + false_positive)
    if (
        true_positive + false_positive
    ) > 0
    else 0
)


# Recall

recall = (
    true_positive /
    (true_positive + false_negative)
    if (
        true_positive + false_negative
    ) > 0
    else 0
)


# F1 Score

f1 = (
    2 * precision * recall /
    (precision + recall)
    if (
        precision + recall
    ) > 0
    else 0
)


print(
    f"\nPrecision: {precision * 100:.2f}%"
)

print(
    f"Recall:    {recall * 100:.2f}%"
)

print(
    f"F1 Score:  {f1 * 100:.2f}%"
)


# ==========================================
# 10. SAVE MODEL
# ==========================================

model_data = {
    "vocabulary": vocabulary,
    "idf": idf,

    "spam_prior": spam_prior,
    "ham_prior": ham_prior,

    "log_spam_prior": log_spam_prior,
    "log_ham_prior": log_ham_prior,

    "log_spam_word_probability":
        log_spam_word_probability,

    "log_ham_word_probability":
        log_ham_word_probability
}


with open(
    "model/spam_model.pkl",
    "wb"
) as file:

    pickle.dump(
        model_data,
        file
    )


print("\n==========================================")
print("MODEL SAVED SUCCESSFULLY!")
print("==========================================")

print("\nCreated:")
print("model/spam_model.pkl")

print("\nSpam detection model is ready! 🚀")
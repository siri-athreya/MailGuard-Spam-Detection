const messageInput =
    document.getElementById("messageInput");

const charCount =
    document.getElementById("charCount");

const clearButton =
    document.getElementById("clearButton");

const analyzeButton =
    document.getElementById("analyzeButton");

const resultSection =
    document.getElementById("resultSection");

const resultIcon =
    document.getElementById("resultIcon");

const resultLabel =
    document.getElementById("resultLabel");

const resultTitle =
    document.getElementById("resultTitle");

const resultDescription =
    document.getElementById("resultDescription");

const confidence =
    document.getElementById("confidence");

const messageLength =
    document.getElementById("messageLength");


// ==========================================
// CHARACTER COUNTER
// ==========================================

messageInput.addEventListener(
    "input",
    () => {

        const length =
            messageInput.value.length;

        charCount.textContent =
            `${length.toLocaleString()} / 10,000`;
    }
);


// ==========================================
// CLEAR BUTTON
// ==========================================

clearButton.addEventListener(
    "click",
    () => {

        messageInput.value = "";

        charCount.textContent =
            "0 / 10,000";

        resultSection.classList.add(
            "hidden"
        );

        messageInput.focus();
    }
);


// ==========================================
// EXAMPLE BUTTONS
// ==========================================

const exampleButtons =
    document.querySelectorAll(
        ".example-button"
    );


exampleButtons.forEach(
    button => {

        button.addEventListener(
            "click",
            () => {

                messageInput.value =
                    button.dataset.message;

                charCount.textContent =
                    `${messageInput.value.length} / 10,000`;

                resultSection.classList.add(
                    "hidden"
                );

                messageInput.focus();
            }
        );
    }
);


// ==========================================
// ANALYZE MESSAGE
// ==========================================

analyzeButton.addEventListener(
    "click",
    async () => {

        const message =
            messageInput.value.trim();


        if (!message) {

            messageInput.focus();

            alert(
                "Please enter an email message first."
            );

            return;
        }


        // Loading state

        analyzeButton.classList.add(
            "loading"
        );

        analyzeButton.innerHTML =
            `
            <span class="button-icon">◌</span>
            Analyzing message...
            <span class="arrow">...</span>
            `;


        try {

            const response =
                await fetch(
                    "/predict",
                    {
                        method: "POST",

                        headers: {
                            "Content-Type":
                                "application/json"
                        },

                        body: JSON.stringify({
                            message: message
                        })
                    }
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.error ||
                    "Something went wrong."
                );
            }


            displayResult(data);


        } catch (error) {

            alert(
                error.message
            );


        } finally {

            analyzeButton.classList.remove(
                "loading"
            );

            analyzeButton.innerHTML =
                `
                <span class="button-icon">✦</span>
                Analyze Message
                <span class="arrow">→</span>
                `;
        }
    }
);


// ==========================================
// DISPLAY RESULT
// ==========================================

function displayResult(data) {

    resultSection.classList.remove(
        "hidden",
        "spam",
        "safe"
    );


    const isSpam =
        data.prediction === "SPAM";


    if (isSpam) {

        resultSection.classList.add(
            "spam"
        );

        resultIcon.textContent =
            "🚨";

        resultLabel.textContent =
            "THREAT DETECTED";

        resultTitle.textContent =
            "SPAM DETECTED";

        resultDescription.textContent =
            "This message contains patterns commonly associated with spam or unwanted messages.";

    } else {

        resultSection.classList.add(
            "safe"
        );

        resultIcon.textContent =
            "✓";

        resultLabel.textContent =
            "ANALYSIS COMPLETE";

        resultTitle.textContent =
            "MESSAGE APPEARS SAFE";

        resultDescription.textContent =
            "Our model did not detect significant spam characteristics in this message.";
    }


    // ======================================
    // BASIC STATISTICS
    // ======================================

    confidence.textContent =
        `${data.confidence}%`;

    messageLength.textContent =
        `${data.message_length.toLocaleString()} chars`;


    // ======================================
    // WORD COUNT
    // ======================================

    let wordCountElement =
        document.getElementById(
            "wordCount"
        );


    if (!wordCountElement) {

        const stats =
            document.querySelector(
                ".result-stats"
            );


        const stat =
            document.createElement(
                "div"
            );

        stat.className =
            "stat";

        stat.innerHTML =
            `
            <span class="stat-label">
                Word Count
            </span>

            <strong id="wordCount">
                —
            </strong>
            `;

        stats.appendChild(stat);

        wordCountElement =
            document.getElementById(
                "wordCount"
            );
    }


    wordCountElement.textContent =
        `${data.word_count} words`;


    // ======================================
    // SPAM INDICATORS
    // ======================================

    let indicatorsContainer =
        document.getElementById(
            "indicatorsContainer"
        );


    if (!indicatorsContainer) {

        indicatorsContainer =
            document.createElement(
                "div"
            );

        indicatorsContainer.id =
            "indicatorsContainer";

        indicatorsContainer.className =
            "indicators-container";

        resultSection.appendChild(
            indicatorsContainer
        );
    }


    indicatorsContainer.innerHTML =
        `
        <div class="indicators-title">
            Detection Insights
        </div>

        <div class="indicator-list">
            ${data.indicators.map(
                indicator => `
                    <span class="indicator">
                        ⚠ ${indicator}
                    </span>
                `
            ).join("")}
        </div>
        `;


    // ======================================
    // CONFIDENCE BAR
    // ======================================

    let confidenceBar =
        document.getElementById(
            "confidenceBar"
        );


    if (!confidenceBar) {

        const barContainer =
            document.createElement(
                "div"
            );

        barContainer.className =
            "confidence-container";

        barContainer.innerHTML =
            `
            <div class="confidence-heading">

                <span>
                    Detection Confidence
                </span>

                <strong id="confidenceBarValue">
                    0%
                </strong>

            </div>

            <div class="confidence-track">

                <div
                    id="confidenceBar"
                    class="confidence-fill">
                </div>

            </div>
            `;

        resultSection.appendChild(
            barContainer
        );

        confidenceBar =
            document.getElementById(
                "confidenceBar"
            );
    }


    const confidenceBarValue =
        document.getElementById(
            "confidenceBarValue"
        );


    confidenceBarValue.textContent =
        `${data.confidence}%`;


    // Small delay for animation

    setTimeout(
        () => {

            confidenceBar.style.width =
                `${data.confidence}%`;

        },
        50
    );


    // ======================================
    // SCROLL TO RESULT
    // ======================================

    resultSection.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}

// ==========================================
// ANALYZE ANOTHER MESSAGE
// ==========================================

const analyzeAgainButton =
    document.getElementById("analyzeAgainButton");

if (analyzeAgainButton) {

    analyzeAgainButton.addEventListener(
        "click",
        () => {

            messageInput.value = "";

            charCount.textContent =
                "0 / 10,000";

            resultSection.classList.add(
                "hidden"
            );

            messageInput.focus();

            window.scrollTo({
                top: 0,
                behavior: "smooth"
            });
        }
    );
}
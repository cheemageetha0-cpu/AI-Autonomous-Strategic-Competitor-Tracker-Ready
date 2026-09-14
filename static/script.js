/* ============================================================
   AI AUTONOMOUS STRATEGIC COMPETITOR TRACKER
   DYNAMIC VISUALIZATION ENGINE
   ============================================================ */

let analysisData = null;

let scoreChart = null;
let radarChart = null;
let gapChart = null;


/* ============================================================
   BASIC HELPERS
   ============================================================ */

function safeArray(value) {

    if (Array.isArray(value)) {
        return value;
    }

    if (value === null || value === undefined) {
        return [];
    }

    return [value];
}


function cleanText(value, fallback = "") {

    if (
        value === null ||
        value === undefined
    ) {
        return fallback;
    }

    if (typeof value === "string") {
        return value;
    }

    return String(value);
}


function numberValue(value, fallback = 0) {

    const n = Number(value);

    if (Number.isFinite(n)) {
        return n;
    }

    return fallback;
}


function escapeHTML(value) {

    return cleanText(value)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}


/* ============================================================
   FIND DATA FROM DIFFERENT POSSIBLE API FIELD NAMES
   ============================================================ */

function getFirst(obj, keys, fallback = null) {

    if (!obj || typeof obj !== "object") {
        return fallback;
    }

    for (const key of keys) {

        if (
            obj[key] !== undefined &&
            obj[key] !== null
        ) {
            return obj[key];
        }
    }

    return fallback;
}


/* ============================================================
   PAGE INITIALIZATION
   ============================================================ */

document.addEventListener("DOMContentLoaded", () => {

    loadAnalysisData();

});


async function loadAnalysisData() {

    /*
       First try data passed through Flask.
    */

    const flaskData =
        window.analysisData ||
        window.ANALYSIS_DATA ||
        null;


    if (flaskData) {

        analysisData = flaskData;

        renderDashboard(analysisData);

        return;
    }


    /*
       If there is no Flask object, try sessionStorage.
    */

    const stored =
        sessionStorage.getItem("analysisData");


    if (stored) {

        try {

            analysisData = JSON.parse(stored);

            renderDashboard(analysisData);

            return;

        } catch (error) {

            console.error(
                "Unable to read stored analysis data:",
                error
            );

        }

    }


    /*
       If no data exists, show a helpful message.
    */

    console.warn(
        "No analysis data was found."
    );

}


/* ============================================================
   MAIN DASHBOARD RENDER
   ============================================================ */

function renderDashboard(data) {

    analysisData = data || {};


    renderSummary(data);

    renderCompetitors(data);

    renderSignals(data);

    renderAdvantages(data);

    renderDevelopments(data);

    renderThreats(data);

    renderOpportunities(data);

    renderMarketGaps(data);

    renderRecommendations(data);

    renderSWOT(data);

    createDynamicGraphs(data);

}


/* ============================================================
   SUMMARY
   ============================================================ */

function renderSummary(data) {

    const idea = getFirst(
        data,
        [
            "business_idea",
            "businessIdea",
            "idea",
            "business",
            "field"
        ],
        "Business"
    );


    const state = getFirst(
        data,
        [
            "state",
            "market",
            "location"
        ],
        "Selected Market"
    );


    const competitors = safeArray(
        getFirst(
            data,
            [
                "competitors",
                "competitor_results",
                "results"
            ],
            []
        )
    );


    const score = numberValue(
        getFirst(
            data,
            [
                "strategic_score",
                "score",
                "target_score"
            ],
            0
        )
    );


    setText(
        "businessName",
        idea
    );

    setText(
        "marketState",
        state
    );

    setText(
        "competitorCount",
        competitors.length
    );

    setText(
        "strategicScore",
        `${score.toFixed(1)}/10`
    );


    const threat = cleanText(
        getFirst(
            data,
            [
                "threat_level",
                "threat"
            ],
            "Unknown"
        )
    );


    setText(
        "threatLevel",
        threat
    );


    setText(
        "threatExplanation",
        getFirst(
            data,
            [
                "threat_explanation",
                "threat_description"
            ],
            "The threat level is calculated from competitor strength, market signals and strategic activity."
        )
    );


    updateThreatMeter(threat);
}


function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent =
            cleanText(value);
    }
}


/* ============================================================
   THREAT METER
   ============================================================ */

function updateThreatMeter(threat) {

    const progress =
        document.getElementById(
            "threatProgress"
        );

    if (!progress) {
        return;
    }


    const text =
        cleanText(threat)
        .toLowerCase();


    let width = 35;


    if (text.includes("high")) {
        width = 90;
    }

    else if (text.includes("medium")) {
        width = 60;
    }

    else if (text.includes("low")) {
        width = 30;
    }


    progress.style.width =
        `${width}%`;
}


/* ============================================================
   COMPETITOR CARDS
   ============================================================ */

function renderCompetitors(data) {

    const container =
        document.getElementById(
            "competitorContainer"
        );

    if (!container) {
        return;
    }


    const competitors =
        safeArray(
            getFirst(
                data,
                [
                    "competitors",
                    "competitor_results",
                    "results"
                ],
                []
            )
        );


    if (!competitors.length) {

        container.innerHTML =
            `<div class="empty-card">
                No competitors were returned.
             </div>`;

        return;
    }


    container.innerHTML =
        competitors.map(
            (competitor, index) => {

                const name =
                    getFirst(
                        competitor,
                        [
                            "name",
                            "company",
                            "company_name",
                            "title"
                        ],
                        `Competitor ${index + 1}`
                    );


                const score =
                    numberValue(
                        getFirst(
                            competitor,
                            [
                                "strategic_score",
                                "score"
                            ],
                            0
                        )
                    );


                const threat =
                    getFirst(
                        competitor,
                        [
                            "threat_level",
                            "threat"
                        ],
                        "Unknown"
                    );


                const description =
                    getFirst(
                        competitor,
                        [
                            "description",
                            "summary",
                            "about"
                        ],
                        "Competitor identified through autonomous analysis."
                    );


                return `
                    <div class="competitor-card">

                        <div class="competitor-top">

                            <div class="competitor-rank">
                                #${index + 1}
                            </div>

                            <div>

                                <h3>
                                    ${escapeHTML(name)}
                                </h3>

                                <span class="competitor-threat">
                                    ${escapeHTML(threat)}
                                </span>

                            </div>

                        </div>


                        <p>
                            ${escapeHTML(description)}
                        </p>


                        <div class="competitor-score">

                            <div>

                                <span>
                                    Strategic score
                                </span>

                                <strong>
                                    ${score.toFixed(1)}/10
                                </strong>

                            </div>

                            <div class="mini-progress">

                                <div style="
                                    width:${Math.max(
                                        0,
                                        Math.min(
                                            100,
                                            score * 10
                                        )
                                    )}%;
                                "></div>

                            </div>

                        </div>

                    </div>
                `;

            }
        ).join("");
}


/* ============================================================
   GRAPH DATA PREPARATION
   ============================================================ */

function getCompetitorScores(data) {

    const competitors =
        safeArray(
            getFirst(
                data,
                [
                    "competitors",
                    "competitor_results",
                    "results"
                ],
                []
            )
        );


    return competitors.map(
        (competitor, index) => {

            const name =
                getFirst(
                    competitor,
                    [
                        "name",
                        "company",
                        "company_name",
                        "title"
                    ],
                    `Competitor ${index + 1}`
                );


            const score =
                numberValue(
                    getFirst(
                        competitor,
                        [
                            "strategic_score",
                            "score"
                        ],
                        0
                    )
                );


            return {
                name: cleanText(name),
                score: score
            };

        }
    );
}


/* ============================================================
   CAPABILITY DATA
   ============================================================ */

function getCapabilityData(data) {

    /*
       Supports:
       capabilities
       capability_scores
       capability_analysis
       dimensions
    */

    const raw =
        getFirst(
            data,
            [
                "capabilities",
                "capability_scores",
                "capability_analysis",
                "dimensions"
            ],
            null
        );


    if (
        raw &&
        typeof raw === "object" &&
        !Array.isArray(raw)
    ) {

        const labels =
            Object.keys(raw);


        return labels.map(
            label => {

                const item =
                    raw[label];


                if (
                    typeof item === "object" &&
                    item !== null
                ) {

                    return {

                        label: label,

                        target:
                            numberValue(
                                getFirst(
                                    item,
                                    [
                                        "target",
                                        "business",
                                        "your_business",
                                        "score"
                                    ],
                                    0
                                )
                            ),

                        competitor:
                            numberValue(
                                getFirst(
                                    item,
                                    [
                                        "competitor",
                                        "competitor_average",
                                        "average",
                                        "benchmark"
                                    ],
                                    0
                                )
                            )

                    };

                }


                return {

                    label: label,

                    target:
                        numberValue(item),

                    competitor:
                        numberValue(item)

                };

            }
        );

    }


    /*
       Fallback capability dimensions.
       These values are only used if the backend does not
       provide capability scores.
    */

    const defaultLabels = [

        "Innovation",
        "Technology",
        "Customer Experience",
        "Personalization",
        "Pricing",
        "Marketing"

    ];


    return defaultLabels.map(
        label => ({

            label: label,

            target:
                getTargetCapability(
                    data,
                    label
                ),

            competitor:
                getCompetitorCapability(
                    data,
                    label
                )

        })
    );
}


/* ============================================================
   TARGET CAPABILITY EXTRACTION
   ============================================================ */

function getTargetCapability(data, label) {

    const keyMap = {

        "Innovation":
            [
                "innovation",
                "innovation_score"
            ],

        "Technology":
            [
                "technology",
                "technology_score",
                "tech_score"
            ],

        "Customer Experience":
            [
                "customer_experience",
                "customer_experience_score"
            ],

        "Personalization":
            [
                "personalization",
                "personalization_score"
            ],

        "Pricing":
            [
                "pricing",
                "pricing_score"
            ],

        "Marketing":
            [
                "marketing",
                "marketing_score"
            ]

    };


    const value =
        getFirst(
            data,
            keyMap[label] || [],
            null
        );


    if (value !== null) {

        return Math.max(
            0,
            Math.min(
                10,
                numberValue(value)
            )
        );

    }


    return 5;
}


/* ============================================================
   COMPETITOR CAPABILITY EXTRACTION
   ============================================================ */

function getCompetitorCapability(data, label) {

    const average =
        getFirst(
            data,
            [
                "competitor_average",
                "average_competitor_score"
            ],
            null
        );


    if (
        average !== null &&
        typeof average === "object"
    ) {

        return numberValue(
            getFirst(
                average,
                [
                    label,
                    label.toLowerCase()
                ],
                6
            )
        );

    }


    return 6;
}


/* ============================================================
   CREATE ALL DYNAMIC GRAPHS
   ============================================================ */

function createDynamicGraphs(data) {

    createScoreChart(data);

    createRadarChart(data);

    createGapChart(data);

}


/* ============================================================
   GRAPH 1 — STRATEGIC SCORE
   ============================================================ */

function createScoreChart(data) {

    const canvas =
        document.getElementById(
            "scoreChart"
        );


    if (!canvas) {
        return;
    }


    if (scoreChart) {
        scoreChart.destroy();
    }


    const competitors =
        getCompetitorScores(data);


    const targetName =
        getFirst(
            data,
            [
                "business_idea",
                "businessIdea",
                "idea",
                "business",
                "field"
            ],
            "Your Business"
        );


    const targetScore =
        numberValue(
            getFirst(
                data,
                [
                    "strategic_score",
                    "target_score",
                    "score"
                ],
                0
            )
        );


    const labels =
        [
            targetName,
            ...competitors.map(
                item => item.name
            )
        ];


    const values =
        [
            targetScore,
            ...competitors.map(
                item => item.score
            )
        ];


    scoreChart =
        new Chart(
            canvas.getContext("2d"),
            {

                type: "bar",

                data: {

                    labels: labels,

                    datasets: [

                        {
                            label:
                                "Strategic Score",

                            data:
                                values,

                            borderRadius: 12,

                            borderWidth: 0,

                            barPercentage: 0.62,

                            categoryPercentage: 0.72

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: {

                        duration: 1400,

                        easing: "easeOutQuart"

                    },

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    function(context) {

                                        return ` Strategic score: ${Number(
                                            context.raw
                                        ).toFixed(1)}/10`;

                                    }

                            }

                        }

                    },

                    scales: {

                        y: {

                            beginAtZero: true,

                            max: 10,

                            ticks: {

                                stepSize: 1

                            },

                            title: {

                                display: true,

                                text:
                                    "Strategic strength"

                            }

                        },

                        x: {

                            title: {

                                display: true,

                                text:
                                    "Business / competitor"

                            }

                        }

                    }

                }

            }
        );


    updateScoreExplanation(
        targetScore,
        competitors
    );
}


/* ============================================================
   SCORE EXPLANATION
   ============================================================ */

function updateScoreExplanation(
    targetScore,
    competitors
) {

    const scores =
        competitors
            .map(item => item.score)
            .filter(
                value => Number.isFinite(value)
            );


    let average = 0;


    if (scores.length) {

        average =
            scores.reduce(
                (a, b) => a + b,
                0
            ) / scores.length;

    }


    const difference =
        targetScore - average;


    const step3 =
        document.getElementById(
            "scoreStep3"
        );


    const step4 =
        document.getElementById(
            "scoreStep4"
        );


    if (step3) {

        if (difference >= 0) {

            step3.textContent =
                `Your strategic score is ${difference.toFixed(
                    1
                )} points above the competitor average. This indicates a comparatively strong strategic position.`;

        }

        else {

            step3.textContent =
                `Your strategic score is ${Math.abs(
                    difference
                ).toFixed(
                    1
                )} points below the competitor average. This indicates a competitive gap that should be investigated.`;

        }

    }


    if (step4) {

        if (difference < 0) {

            step4.textContent =
                `The current gap is approximately ${Math.abs(
                    difference
                ).toFixed(
                    1
                )} points. Focus first on the capability areas shown in the Capability Gap Analysis.`;

        }

        else {

            step4.textContent =
                `Your overall strategic score is currently at or above the competitor average. Continue strengthening the areas where competitors remain ahead.`;

        }

    }

}


/* ============================================================
   GRAPH 2 — RADAR
   ============================================================ */

function createRadarChart(data) {

    const canvas =
        document.getElementById(
            "radarChart"
        );


    if (!canvas) {
        return;
    }


    if (radarChart) {
        radarChart.destroy();
    }


    const capabilities =
        getCapabilityData(data);


    const labels =
        capabilities.map(
            item => item.label
        );


    const target =
        capabilities.map(
            item =>
                Math.max(
                    0,
                    Math.min(
                        10,
                        numberValue(
                            item.target
                        )
                    )
                )
        );


    const competitor =
        capabilities.map(
            item =>
                Math.max(
                    0,
                    Math.min(
                        10,
                        numberValue(
                            item.competitor
                        )
                    )
                )
        );


    radarChart =
        new Chart(
            canvas.getContext("2d"),
            {

                type: "radar",

                data: {

                    labels: labels,

                    datasets: [

                        {

                            label:
                                "Your Business",

                            data:
                                target,

                            borderWidth: 3,

                            pointRadius: 5,

                            pointHoverRadius: 8,

                            fill: true

                        },

                        {

                            label:
                                "Competitor Average",

                            data:
                                competitor,

                            borderWidth: 3,

                            pointRadius: 5,

                            pointHoverRadius: 8,

                            fill: true

                        }

                    ]

                },

                options: {

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: {

                        duration: 1600,

                        easing: "easeOutQuart"

                    },

                    plugins: {

                        legend: {

                            position:
                                "bottom"

                        }

                    },

                    scales: {

                        r: {

                            beginAtZero: true,

                            min: 0,

                            max: 10,

                            ticks: {

                                stepSize: 2

                            },

                            pointLabels: {

                                font: {

                                    size: 12,

                                    weight: "600"

                                }

                            }

                        }

                    }

                }

            }
        );


    renderCapabilitySummary(
        capabilities
    );

    updateRadarExplanation(
        capabilities
    );
}


/* ============================================================
   CAPABILITY SUMMARY
   ============================================================ */

function renderCapabilitySummary(
    capabilities
) {

    const container =
        document.getElementById(
            "capabilityList"
        );


    if (!container) {
        return;
    }


    container.innerHTML =
        capabilities.map(
            item => {

                const gap =
                    numberValue(
                        item.target
                    ) -
                    numberValue(
                        item.competitor
                    );


                const status =
                    gap >= 0
                        ? "Strength"
                        : "Gap";


                return `

                    <div class="capability-row">

                        <div class="capability-row-top">

                            <strong>
                                ${escapeHTML(
                                    item.label
                                )}
                            </strong>

                            <span class="${
                                gap >= 0
                                    ? "positive"
                                    : "negative"
                            }">

                                ${status}

                            </span>

                        </div>


                        <div class="capability-values">

                            <span>
                                You:
                                <strong>
                                    ${numberValue(
                                        item.target
                                    ).toFixed(1)}
                                </strong>
                            </span>

                            <span>
                                Competitors:
                                <strong>
                                    ${numberValue(
                                        item.competitor
                                    ).toFixed(1)}
                                </strong>
                            </span>

                        </div>

                    </div>

                `;

            }
        ).join("");
}


/* ============================================================
   RADAR EXPLANATION
   ============================================================ */

function updateRadarExplanation(
    capabilities
) {

    const step4 =
        document.getElementById(
            "radarStep4"
        );


    if (!step4) {
        return;
    }


    const gaps =
        capabilities
            .map(
                item => ({

                    label:
                        item.label,

                    gap:
                        numberValue(
                            item.competitor
                        ) -
                        numberValue(
                            item.target
                        )

                })
            )
            .filter(
                item => item.gap > 0
            )
            .sort(
                (a, b) =>
                    b.gap - a.gap
            );


    if (!gaps.length) {

        step4.textContent =
            "Your business is currently equal to or ahead of the competitor benchmark across the displayed capability dimensions.";

        return;
    }


    const top =
        gaps
            .slice(0, 3)
            .map(
                item =>
                    `${item.label} (${item.gap.toFixed(1)} points)`
            )
            .join(", ");


    step4.textContent =
        `The largest competitor advantages are ${top}. These areas should receive attention first.`;
}


/* ============================================================
   GRAPH 3 — GAP ANALYSIS
   ============================================================ */

function createGapChart(data) {

    const canvas =
        document.getElementById(
            "gapChart"
        );


    if (!canvas) {
        return;
    }


    if (gapChart) {
        gapChart.destroy();
    }


    const capabilities =
        getCapabilityData(data);


    const gaps =
        capabilities.map(
            item => ({

                label:
                    item.label,

                gap:
                    numberValue(
                        item.competitor
                    ) -
                    numberValue(
                        item.target
                    )

            })
        );


    gapChart =
        new Chart(
            canvas.getContext("2d"),
            {

                type: "bar",

                data: {

                    labels:
                        gaps.map(
                            item =>
                                item.label
                        ),

                    datasets: [

                        {

                            label:
                                "Competitor advantage",

                            data:
                                gaps.map(
                                    item =>
                                        Number(
                                            item.gap.toFixed(
                                                2
                                            )
                                        )
                                ),

                            borderRadius: 10,

                            borderWidth: 0,

                            barPercentage: 0.58,

                            categoryPercentage: 0.7

                        }

                    ]

                },

                options: {

                    indexAxis: "y",

                    responsive: true,

                    maintainAspectRatio: false,

                    animation: {

                        duration: 1500,

                        easing: "easeOutQuart"

                    },

                    plugins: {

                        legend: {

                            display: false

                        },

                        tooltip: {

                            callbacks: {

                                label:
                                    function(context) {

                                        const value =
                                            Number(
                                                context.raw
                                            );

                                        if (value > 0) {

                                            return ` Competitors lead by ${value.toFixed(
                                                1
                                            )} points`;

                                        }

                                        if (value < 0) {

                                            return ` Your business leads by ${Math.abs(
                                                value
                                            ).toFixed(
                                                1
                                            )} points`;

                                        }

                                        return " No capability gap";

                                    }

                            }

                        }

                    },

                    scales: {

                        x: {

                            title: {

                                display: true,

                                text:
                                    "Capability gap"

                            }

                        }

                    }

                }

            }
        );


    renderGapPriorityCards(
        gaps
    );

    updateGapExplanation(
        gaps
    );
}


/* ============================================================
   GAP PRIORITY CARDS
   ============================================================ */

function renderGapPriorityCards(
    gaps
) {

    const container =
        document.getElementById(
            "gapPriorityCards"
        );


    if (!container) {
        return;
    }


    const priority =
        gaps
            .filter(
                item => item.gap > 0
            )
            .sort(
                (a, b) =>
                    b.gap - a.gap
            );


    if (!priority.length) {

        container.innerHTML = `

            <div class="priority-card success">

                <span>✓</span>

                <div>

                    <strong>
                        No major capability gap detected
                    </strong>

                    <p>
                        Your business is currently at or above
                        the competitor benchmark in the analysed areas.
                    </p>

                </div>

            </div>

        `;

        return;
    }


    container.innerHTML =
        priority
            .slice(0, 4)
            .map(
                (item, index) => `

                    <div class="priority-card">

                        <div class="priority-number">
                            ${index + 1}
                        </div>

                        <div>

                            <strong>
                                ${escapeHTML(
                                    item.label
                                )}
                            </strong>

                            <p>
                                Competitors lead by
                                <b>
                                    ${item.gap.toFixed(
                                        1
                                    )}
                                </b>
                                points.
                            </p>

                        </div>

                    </div>

                `
            )
            .join("");
}


/* ============================================================
   GAP EXPLANATION
   ============================================================ */

function updateGapExplanation(
    gaps
) {

    const step4 =
        document.getElementById(
            "gapStep4"
        );


    if (!step4) {
        return;
    }


    const largest =
        gaps
            .filter(
                item => item.gap > 0
            )
            .sort(
                (a, b) =>
                    b.gap - a.gap
            );


    if (!largest.length) {

        step4.textContent =
            "There is no positive competitor gap in the displayed capabilities. Continue monitoring the market and maintain your strongest areas.";

        return;
    }


    const names =
        largest
            .slice(0, 3)
            .map(
                item =>
                    `${item.label} (${item.gap.toFixed(
                        1
                    )})`
            )
            .join(", ");


    step4.textContent =
        `The highest-priority gaps are ${names}. These should be considered first when planning improvements.`;
}


/* ============================================================
   STRATEGIC SIGNALS
   ============================================================ */

function renderSignals(data) {

    const container =
        document.getElementById(
            "signalsContainer"
        );


    if (!container) {
        return;
    }


    let signals =
        safeArray(
            getFirst(
                data,
                [
                    "strategic_signals",
                    "signals"
                ],
                []
            )
        );


    if (!signals.length) {

        signals = [

            "Competitor technology activity detected.",

            "Customer experience remains an important competitive factor.",

            "Product differentiation can create strategic advantage."

        ];

    }


    container.innerHTML =
        signals.map(
            signal => `

                <div class="signal-card">

                    <div class="signal-icon">
                        ⚡
                    </div>

                    <p>
                        ${escapeHTML(
                            typeof signal === "object"
                                ? getFirst(
                                    signal,
                                    [
                                        "text",
                                        "description",
                                        "signal"
                                    ],
                                    ""
                                )
                                : signal
                        )}
                    </p>

                </div>

            `
        ).join("");
}


/* ============================================================
   ADVANTAGES
   ============================================================ */

function renderAdvantages(data) {

    const container =
        document.getElementById(
            "advantagesContainer"
        );


    if (!container) {
        return;
    }


    const competitors =
        safeArray(
            getFirst(
                data,
                [
                    "competitors",
                    "competitor_results",
                    "results"
                ],
                []
            )
        );


    const advantages = [];


    competitors.forEach(
        competitor => {

            const name =
                getFirst(
                    competitor,
                    [
                        "name",
                        "company",
                        "company_name"
                    ],
                    "Competitor"
                );


            const strengths =
                safeArray(
                    getFirst(
                        competitor,
                        [
                            "advantages",
                            "strengths",
                            "why_better"
                        ],
                        []
                    )
                );


            strengths.forEach(
                strength => {

                    advantages.push({

                        name:
                            name,

                        text:
                            typeof strength === "object"
                                ? getFirst(
                                    strength,
                                    [
                                        "text",
                                        "description"
                                    ],
                                    ""
                                )
                                : strength

                    });

                }
            );

        }
    );


    if (!advantages.length) {

        container.innerHTML = `

            <div class="info-card">

                <div class="info-icon">
                    💡
                </div>

                <div>

                    <h3>
                        Competitive positioning
                    </h3>

                    <p>
                        Competitors may be stronger because
                        of product differentiation, technology,
                        customer experience, pricing or market reach.
                    </p>

                </div>

            </div>

        `;

        return;
    }


    container.innerHTML =
        advantages
            .slice(0, 12)
            .map(
                item => `

                    <div class="info-card">

                        <div class="info-icon">
                            💡
                        </div>

                        <div>

                            <span class="info-company">
                                ${escapeHTML(
                                    item.name
                                )}
                            </span>

                            <p>
                                ${escapeHTML(
                                    item.text
                                )}
                            </p>

                        </div>

                    </div>

                `
            )
            .join("");
}


/* ============================================================
   DEVELOPMENTS
   ============================================================ */

function renderDevelopments(data) {

    const container =
        document.getElementById(
            "developmentContainer"
        );


    if (!container) {
        return;
    }


    const developments =
        safeArray(
            getFirst(
                data,
                [
                    "developments",
                    "competitor_developments",
                    "launches"
                ],
                []
            )
        );


    if (!developments.length) {

        container.innerHTML = `

            <div class="empty-card">

                No specific competitor developments
                were returned by the analysis.

            </div>

        `;

        return;
    }


    container.innerHTML =
        developments
            .map(
                item => {

                    const title =
                        typeof item === "object"
                            ? getFirst(
                                item,
                                [
                                    "title",
                                    "name",
                                    "development"
                                ],
                                "Development"
                            )
                            : "Competitor Development";


                    const text =
                        typeof item === "object"
                            ? getFirst(
                                item,
                                [
                                    "description",
                                    "details",
                                    "summary"
                                ],
                                ""
                            )
                            : item;


                    return `

                        <div class="development-card">

                            <div class="development-icon">
                                🚀
                            </div>

                            <div>

                                <h3>
                                    ${escapeHTML(
                                        title
                                    )}
                                </h3>

                                <p>
                                    ${escapeHTML(
                                        text
                                    )}
                                </p>

                            </div>

                        </div>

                    `;

                }
            )
            .join("");
}


/* ============================================================
   THREATS
   ============================================================ */

function renderThreats(data) {

    const container =
        document.getElementById(
            "threatContainer"
        );


    if (!container) {
        return;
    }


    const threats =
        safeArray(
            getFirst(
                data,
                [
                    "threats",
                    "competitive_threats"
                ],
                []
            )
        );


    if (!threats.length) {

        container.innerHTML =
            `<p class="empty-text">
                No additional threats were returned.
             </p>`;

        return;
    }


    container.innerHTML =
        threats
            .map(
                threat => `

                    <div class="list-item">

                        <span class="list-icon">
                            ⚠️
                        </span>

                        <p>
                            ${escapeHTML(
                                typeof threat === "object"
                                    ? getFirst(
                                        threat,
                                        [
                                            "text",
                                            "description",
                                            "threat"
                                        ],
                                        ""
                                    )
                                    : threat
                            )}
                        </p>

                    </div>

                `
            )
            .join("");
}


/* ============================================================
   OPPORTUNITIES
   ============================================================ */

function renderOpportunities(data) {

    const container =
        document.getElementById(
            "opportunityContainer"
        );


    if (!container) {
        return;
    }


    const opportunities =
        safeArray(
            getFirst(
                data,
                [
                    "opportunities",
                    "growth_opportunities"
                ],
                []
            )
        );


    if (!opportunities.length) {

        container.innerHTML =
            `<p class="empty-text">
                No additional opportunities were returned.
             </p>`;

        return;
    }


    container.innerHTML =
        opportunities
            .map(
                opportunity => `

                    <div class="list-item">

                        <span class="list-icon">
                            🌱
                        </span>

                        <p>
                            ${escapeHTML(
                                typeof opportunity === "object"
                                    ? getFirst(
                                        opportunity,
                                        [
                                            "text",
                                            "description",
                                            "opportunity"
                                        ],
                                        ""
                                    )
                                    : opportunity
                            )}
                        </p>

                    </div>

                `
            )
            .join("");
}


/* ============================================================
   MARKET GAP DETECTOR
   ============================================================ */

function renderMarketGaps(data) {

    const container = document.getElementById("marketGapContainer");

    if (!container) {
        return;
    }

    const gaps = safeArray(getFirst(data, ["market_gaps", "marketGaps"], []));

    if (!gaps.length) {
        container.innerHTML = `
            <div class="empty-card">
                Not enough competitor data to identify reliable market gaps.
            </div>
        `;
        return;
    }

    container.innerHTML = gaps.map(gap => {
        const strength = Math.max(0, Math.min(100, numberValue(gap.strength, 0)));
        const level = cleanText(gap.level, strength >= 70 ? "High Opportunity" : strength >= 45 ? "Medium Opportunity" : "Low Opportunity");
        const levelClass = strength >= 70 ? "high" : strength >= 45 ? "medium" : "low";

        return `
            <article class="market-gap-card ${levelClass}">
                <div class="market-gap-top">
                    <div>
                        <span class="gap-level ${levelClass}">${escapeHTML(level)}</span>
                        <h3>${escapeHTML(gap.title)}</h3>
                    </div>
                    <strong>${strength}%</strong>
                </div>
                <div class="market-gap-progress" aria-label="Gap strength ${strength}%">
                    <span style="width: ${strength}%"></span>
                </div>
                <div class="market-gap-detail">
                    <strong>Why This Gap Matters</strong>
                    <p>${escapeHTML(gap.why_matters)}</p>
                </div>
                <div class="market-gap-detail">
                    <strong>💡 Business Opportunity</strong>
                    <p>${escapeHTML(gap.business_opportunity)}</p>
                </div>
                <div class="market-gap-detail differentiator">
                    <strong>🎯 Recommended Differentiator</strong>
                    <p>${escapeHTML(gap.recommended_differentiator)}</p>
                </div>
            </article>
        `;
    }).join("");
}


/* ============================================================
   RECOMMENDATIONS
   ============================================================ */

function renderRecommendations(data) {

    const container =
        document.getElementById(
            "recommendationContainer"
        );


    if (!container) {
        return;
    }


    const recommendations =
        safeArray(
            getFirst(
                data,
                [
                    "recommendations",
                    "strategic_recommendations",
                    "improvements"
                ],
                []
            )
        );


    if (!recommendations.length) {

        container.innerHTML = `

            <div class="recommendation-card">

                <div class="recommendation-number">
                    1
                </div>

                <div>

                    <h3>
                        Improve differentiation
                    </h3>

                    <p>
                        Create a clear reason for customers
                        to choose your business over competitors.
                    </p>

                </div>

            </div>

        `;

        return;
    }


    container.innerHTML =
        recommendations
            .map(
                (recommendation, index) => {

                    const text =
                        typeof recommendation === "object"
                            ? getFirst(
                                recommendation,
                                [
                                    "text",
                                    "description",
                                    "recommendation"
                                ],
                                ""
                            )
                            : recommendation;


                    return `

                        <div class="recommendation-card">

                            <div class="recommendation-number">
                                ${index + 1}
                            </div>

                            <div>

                                <h3>
                                    Strategic improvement
                                </h3>

                                <p>
                                    ${escapeHTML(
                                        text
                                    )}
                                </p>

                            </div>

                        </div>

                    `;

                }
            )
            .join("");
}


/* ============================================================
   SWOT
   ============================================================ */

function renderSWOT(data) {

    const swot =
        getFirst(
            data,
            [
                "swot",
                "SWOT"
            ],
            {}
        ) || {};


    fillList(
        "strengthList",
        getFirst(
            swot,
            [
                "strengths",
                "Strengths"
            ],
            getFirst(
                data,
                ["strengths"],
                []
            )
        )
    );


    fillList(
        "weaknessList",
        getFirst(
            swot,
            [
                "weaknesses",
                "Weaknesses"
            ],
            getFirst(
                data,
                ["weaknesses"],
                []
            )
        )
    );


    fillList(
        "swotOpportunityList",
        getFirst(
            swot,
            [
                "opportunities",
                "Opportunities"
            ],
            getFirst(
                data,
                ["opportunities"],
                []
            )
        )
    );


    fillList(
        "swotThreatList",
        getFirst(
            swot,
            [
                "threats",
                "Threats"
            ],
            getFirst(
                data,
                ["threats"],
                []
            )
        )
    );
}


function fillList(id, values) {

    const element =
        document.getElementById(id);


    if (!element) {
        return;
    }


    const list =
        safeArray(values);


    element.innerHTML =
        list.map(
            item => `

                <li>
                    ${escapeHTML(
                        typeof item === "object"
                            ? getFirst(
                                item,
                                [
                                    "text",
                                    "description"
                                ],
                                ""
                            )
                            : item
                    )}
                </li>

            `
        ).join("");
}


/* ============================================================
   PDF
   ============================================================ */

async function downloadPDF() {

    if (!analysisData) {

        alert(
            "No analysis data is available for the report."
        );

        return;

    }


    try {

        const response =
            await fetch(
                "/api/report",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify(
                            analysisData
                        )

                }
            );


        if (!response.ok) {

            throw new Error(
                "PDF generation failed."
            );

        }


        const blob =
            await response.blob();


        const url =
            window.URL.createObjectURL(
                blob
            );


        const link =
            document.createElement(
                "a"
            );


        link.href = url;

        link.download =
            "AI_Strategic_Competitor_Report.pdf";


        document.body.appendChild(
            link
        );


        link.click();


        link.remove();


        window.URL.revokeObjectURL(
            url
        );

    }

    catch (error) {

        console.error(error);

        alert(
            "Unable to generate the PDF report."
        );

    }

}


/* ============================================================
   RESIZE / RECREATE GRAPHS
   ============================================================ */

window.addEventListener(
    "resize",
    () => {

        if (scoreChart) {
            scoreChart.resize();
        }

        if (radarChart) {
            radarChart.resize();
        }

        if (gapChart) {
            gapChart.resize();
        }

    }
);

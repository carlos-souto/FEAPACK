/* Basic examples. */
const basic = [
    ["basic1.html", "Basic example #1: Pipe under internal pressure."         ],
    ["basic2.html", "Basic example #2: Plate with a central hole."            ],
    ["basic3.html", "Basic example #3: Analysis of a pressure vessel."        ],
    ["basic4.html", "Basic example #4: Free vibration of a rectangular plate."],
    ["basic5.html", "Basic example #5: Buckling of a slender bar."            ],
];

/* Advanced examples. */
const advanced = [
    ["advanced1.html", "Advanced example #1: Creating a mesh with Gmsh and importing it into FEAPACK." ],
    ["advanced2.html", "Advanced example #2: Incremental mesh refinement and mesh dependency analysis."],
    ["advanced3.html", "Advanced example #3: Stress intensity factors via VCCT."                       ],
    ["advanced4.html", "Advanced example #4: Fatigue crack propagation via VCEM."                      ],
];

/* Lists the examples in the page. */
document.addEventListener("DOMContentLoaded", () => {

    // list examples in dropdown menu
    let dropdown = document.getElementById("dropdown-examples");
    if (dropdown) {
        [...basic, ...advanced].forEach(element => {
            let hyperlink = document.createElement("a");
            hyperlink.href = element[0];
            hyperlink.textContent = element[1];
            dropdown.appendChild(hyperlink);
        });
    }

    // list examples in guide (basic)
    let basicExampleList = document.getElementById("basic-example-list");
    if (basicExampleList) {
        basic.forEach(element => {
            let hyperlink = document.createElement("a");
            hyperlink.href = element[0];
            hyperlink.textContent = element[1];
            let item = document.createElement("li");
            item.appendChild(hyperlink);
            basicExampleList.appendChild(item);
        });
    }

    // list examples in guide (advanced)
    let advancedExampleList = document.getElementById("advanced-example-list");
    if (advancedExampleList) {
        advanced.forEach(element => {
            let hyperlink = document.createElement("a");
            hyperlink.href = element[0];
            hyperlink.textContent = element[1];
            let item = document.createElement("li");
            item.appendChild(hyperlink);
            advancedExampleList.appendChild(item);
        });
    }
});

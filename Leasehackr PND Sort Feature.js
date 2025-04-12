// ==UserScript==
// @name         Leasehackr PND Sort Feature
// @namespace    http://tampermonkey.net/
// @version      0.7.5
// @description  Adds a sort feature
// @author       @itskerv
// @match        https://pnd.leasehackr.com/*
// @grant        none
// @downloadURL  https://raw.githubusercontent.com/itskerv/LeaseHackr/main/Leasehackr%20PND%20Sort%20Feature.user.js
// @updateURL    https://raw.githubusercontent.com/itskerv/LeaseHackr/main/Leasehackr%20PND%20Sort%20Feature.user.js
// ==/UserScript==

(function() {
    'use strict';

    // Flag to prevent the observer from re-triggering sort during our own DOM changes.
    let suppressObserver = false;
    // Store current sort option (always ascending).
    let currentSortOption = "";

    // Wait for required elements: both #avail_locations (Vehicle Location) and at least one .deal_card.
    function initWatcher() {
        const vehicleLoc = document.querySelector('#avail_locations');
        const dealCards = document.querySelectorAll('.deal_card');

        if (!vehicleLoc || dealCards.length === 0) {
            console.log("[Sort Script] Waiting for required elements...");
            setTimeout(initWatcher, 500);
            return;
        }
        console.log("[Sort Script] Required elements found. Initializing sort controls.");
        addSortDropdown();
        observeDealContainer();
    }

    // Creates and inserts the "Sort By:" dropdown styled similar to the Vehicle Location element.
    function addSortDropdown() {
        // Prevent duplicate insertion if the dropdown already exists.
        if (document.getElementById("sort_options")) {
            console.log("[Sort Script] Sort dropdown already exists; skipping creation.");
            return;
        }

        const sortContainer = document.createElement('div');
        sortContainer.style.display = "flex";
        sortContainer.style.gap = "10px";
        sortContainer.style.alignItems = "center";
        sortContainer.style.marginTop = "10px";

        // "Sort By:" label
        const sortLabel = document.createElement('span');
        sortLabel.className = "filter_label";
        sortLabel.style.margin = "0";
        sortLabel.style.whiteSpace = "nowrap";
        sortLabel.textContent = "Sort By:";

        // The dropdown select element
        const select = document.createElement('select');
        select.id = "sort_options";
        select.className = "sub_filter";
        select.style.padding = "5px";

        // Default disabled option
        const defaultOption = document.createElement('option');
        defaultOption.textContent = "Select sort option";
        defaultOption.value = "";
        defaultOption.disabled = true;
        defaultOption.selected = true;
        select.appendChild(defaultOption);

        // Define sort options
        const sortOptions = [
            { label: "Monthly Payment", type: "price", value: "price" },
            { label: "Monthly Payment w/ Incentives", type: "incentive", value: "incentive" },
            { label: "Expiration Date", type: "expiration", value: "expiration" },
            { label: "MSRP", type: "msrp", value: "msrp" },
            { label: "Quantity Left", type: "quantity", value: "quantity" },
            { label: "Due at Signing", type: "due", value: "due" },
            { label: "Lease Term", type: "term", value: "term" },
            { label: "Mileage Allowance", type: "mileage", value: "mileage" }
        ];

        sortOptions.forEach(optData => {
            const opt = document.createElement('option');
            opt.textContent = optData.label;
            opt.value = optData.value;
            select.appendChild(opt);
        });

        // When a sort option is selected, update and apply the sort.
        select.addEventListener('change', function(e) {
            e.stopPropagation();
            e.preventDefault();
            currentSortOption = this.value;
            console.log(`[Sort Script] User selected: ${currentSortOption}`);
            sortCardsByType(this.value);
        });

        // Append label and select to the container.
        sortContainer.appendChild(sortLabel);
        sortContainer.appendChild(select);

        // Insert the sort container right below the Vehicle Location element.
        const vehicleLocationContainer = document.querySelector('#avail_locations')?.parentNode;
        if (vehicleLocationContainer) {
            vehicleLocationContainer.insertAdjacentElement('afterend', sortContainer);
            console.log("[Sort Script] Sort dropdown inserted.");
        } else {
            document.body.insertBefore(sortContainer, document.body.firstChild);
        }
    }

    // Observes the container holding deal cards and re-applies the chosen sort when new deals load.
    function observeDealContainer() {
        const firstCard = document.querySelector('.deal_card');
        if (!firstCard) {
            console.log("[Sort Script] No .deal_card found for observer; skipping observer setup.");
            return;
        }
        const container = firstCard.parentNode;
        const observer = new MutationObserver(() => {
            if (suppressObserver) return;
            if (currentSortOption) {
                console.log("[Sort Script] Detected new deals. Re-applying sort:", currentSortOption);
                setTimeout(() => {
                    sortCardsByType(currentSortOption);
                }, 100);
            }
        });
        observer.observe(container, { childList: true });
        console.log("[Sort Script] MutationObserver set up on deal cards container.");
    }

    // Sorts the deal cards based on the selected sort type (always ascending).
    function sortCardsByType(sortType) {
        const cards = Array.from(document.querySelectorAll('.deal_card'));
        if (cards.length === 0) {
            console.log("[Sort Script] No deal cards to sort.");
            return;
        }

        console.log(`[Sort Script] Sorting deals by "${sortType}" in ascending order.`);
        suppressObserver = true;

        cards.sort((a, b) => {
            const aVal = getSortValue(a, sortType);
            const bVal = getSortValue(b, sortType);
            return aVal - bVal; // Always ascending
        });

        const parent = cards[0].parentNode;
        cards.forEach(card => parent.removeChild(card));
        cards.forEach(card => parent.appendChild(card));

        suppressObserver = false;
    }

    // Extracts a numeric value from a deal card based on the sort type.
    function getSortValue(card, type) {
        switch (type) {
            case 'price': {
                const priceElem = card.querySelector('.monthly_val');
                if (priceElem) {
                    const val = parseFloat(priceElem.textContent.replace(/[^0-9.]/g, ''));
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            case 'incentive': {
                let incentivePrice = NaN;
                let monthlyPrice = NaN;
                const incentiveElem = card.querySelector('.con_monthly_val');
                if (incentiveElem && incentiveElem.textContent.trim() !== "") {
                    incentivePrice = parseFloat(incentiveElem.textContent.replace(/[^0-9.]/g, ''));
                }
                const monthlyElem = card.querySelector('.monthly_val');
                if (monthlyElem) {
                    monthlyPrice = parseFloat(monthlyElem.textContent.replace(/[^0-9.]/g, ''));
                }
                if (!isNaN(incentivePrice) && !isNaN(monthlyPrice)) {
                    return Math.min(incentivePrice, monthlyPrice);
                } else if (!isNaN(incentivePrice)) {
                    return incentivePrice;
                } else if (!isNaN(monthlyPrice)) {
                    return monthlyPrice;
                }
                return Number.MAX_VALUE;
            }
            case 'expiration': {
                const expElem = card.querySelector('.exp_date_val');
                if (expElem) {
                    const dateStr = expElem.getAttribute('value') || expElem.textContent.trim();
                    const d = new Date(dateStr);
                    if (!isNaN(d.getTime())) return d.getTime();
                }
                return Number.MAX_VALUE;
            }
            case 'msrp': {
                const msrpElem = card.querySelector('.msrp_val');
                if (msrpElem) {
                    const val = parseFloat(msrpElem.textContent.replace(/[^0-9.]/g, ''));
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            case 'quantity': {
                const qtyElem = card.querySelector('.qty_val');
                if (qtyElem) {
                    const val = parseInt(qtyElem.textContent.replace(/[^0-9]/g, ''), 10);
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            case 'due': {
                const dueElem = card.querySelector('.das_val');
                if (dueElem) {
                    const val = parseFloat(dueElem.textContent.replace(/[^0-9.]/g, ''));
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            case 'term': {
                const termElem = card.querySelector('.term_val');
                if (termElem) {
                    const val = parseInt(termElem.textContent.replace(/[^0-9]/g, ''), 10);
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            case 'mileage': {
                const mileageElem = card.querySelector('.mileage_val');
                if (mileageElem) {
                    const val = parseFloat(mileageElem.textContent.replace(/[^0-9.]/g, ''));
                    if (!isNaN(val)) return val;
                }
                return Number.MAX_VALUE;
            }
            default:
                return Number.MAX_VALUE;
        }
    }

    // Start the initialization process.
    initWatcher();
})();

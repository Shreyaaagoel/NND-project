// ==UserScript==
// @name         Sensitive Data Detector Form on httpbin.org
// @namespace    http://tampermonkey.net/
// @version      3.0
// @description  Adds a form to httpbin.org that detects and encrypts sensitive data before submission.
// @author       ChatGPT
// @match        https://httpbin.org/
// @grant        GM_notification
// @grant        GM_addStyle
// ==/UserScript==

(function() {
    'use strict';

    // Regex patterns for detecting sensitive data
    const emailRegex = /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b/;
    const cardRegex = /\b(?:\d[ -]*?){13,16}\b/;

    let encryptionEnabled = false; // Tracks encryption status

    // Create UI for form
    function createUI() {
        if (document.getElementById("sensitive-data-form")) return; // Prevent duplicate forms

        let formContainer = document.createElement("div");
        formContainer.id = "sensitive-data-form";
        formContainer.innerHTML = `
            <h2>🔍 Sensitive Data Checker</h2>
            <label>Email:</label>
            <input type="text" id="emailInput" placeholder="Enter email"><br>
            <label>Credit Card:</label>
            <input type="text" id="cardInput" placeholder="Enter credit card number"><br>
            <button id="encrypt-btn">🔒 Enable Encryption</button>
            <button id="submit-btn">Submit</button>
        `;
        document.body.appendChild(formContainer);

        document.getElementById("encrypt-btn").addEventListener("click", toggleEncryption);
        document.getElementById("submit-btn").addEventListener("click", checkBeforeSubmit);
    }

    // Function to toggle encryption mode
    function toggleEncryption() {
        encryptionEnabled = !encryptionEnabled;
        let btn = document.getElementById("encrypt-btn");
        btn.style.background = encryptionEnabled ? "green" : "gray";
        btn.innerText = encryptionEnabled ? "🔒 Encryption ON" : "❌ Encryption OFF";
    }

    // Function to encrypt sensitive data
    function encryptData(value) {
        return btoa(value); // Base64 encoding
    }

    // Function to check sensitive data before submission
    function checkBeforeSubmit() {
        let email = document.getElementById("emailInput").value;
        let card = document.getElementById("cardInput").value;

        if (!encryptionEnabled) {
            if (emailRegex.test(email) || cardRegex.test(card)) {
                playAlertSound();
                GM_notification({ text: "❌ Sensitive Data Detected! Encrypt before submission.", timeout: 4000 });
                alert("❌ Sensitive Data Detected! Enable encryption before submission.");
                return;
            }
        } else {
            // Encrypt data before submission
            if (email) document.getElementById("emailInput").value = encryptData(email);
            if (card) document.getElementById("cardInput").value = encryptData(card);
            alert("✅ Data Encrypted & Submitted!");
        }
    }

    // Function to play an alert sound
    function playAlertSound() {
        let audio = new Audio("https://www.myinstants.com/media/sounds/error.mp3");
        audio.play();
    }

    // Add CSS for the UI
    GM_addStyle(`
        #sensitive-data-form {
            position: fixed;
            top: 50px;
            right: 10px;
            background: white;
            padding: 15px;
            border: 2px solid black;
            box-shadow: 0px 0px 10px black;
            width: 250px;
            font-size: 14px;
        }
        #sensitive-data-form h2 {
            margin: 0;
            font-size: 16px;
            color: red;
        }
        #sensitive-data-form input {
            width: 100%;
            padding: 5px;
            margin: 5px 0;
            border: 1px solid gray;
        }
        #encrypt-btn, #submit-btn {
            width: 100%;
            padding: 5px;
            margin-top: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        #encrypt-btn {
            background: gray;
            color: white;
            border: none;
        }
        #submit-btn {
            background: blue;
            color: white;
            border: none;
        }
    `);

    // Inject UI on page load
    createUI();

})();

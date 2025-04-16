import { createInventoryItem, updateInventory } from "./inventory.js";

export async function handleResponse(data, endpoint) {
	return new Promise(async (resolve, reject) => {
		var proxyRequest = await fetch(endpoint, {
			method: "POST",
			headers: { "Content-Type": "application/json" },
			body: JSON.stringify(data),
		});
		const responseData = await proxyRequest.json();
		console.log("Result from Python:", responseData);
		resolve(responseData);
	});
}

async function updateAdventureText(response) {
	const adventureText = document.getElementById("adventure-text");
	const actionText = document.createElement("span");
	actionText.innerHTML = response["actionResponse"];
	actionText.style.backgroundColor = "#92523054";
	actionText.className = "action";
	actionText.id = "action" + history.length;
	if (history.length > 0) {
		const lastAction = document.getElementById(history[history.length - 1]);
		lastAction.style.backgroundColor = "transparent";
	}
	history.push(actionText.id);

	adventureText.appendChild(actionText);
}

// Send Player Action
async function handleSend() {
	try {
		const message = document.getElementById("action-input").value;
		const response = await handleResponse(
			{ message },
			"http://127.0.0.1:3000/getaction"
		);

		updateAdventureText(response);
		updateInventory(response);
		console.log("Response from handleResponse:", response);
	} catch (error) {
		console.error("Error in handleResponse:", error);
	}
}

let history = [];

document
	.getElementById("run-action-button")
	.addEventListener("click", handleSend);

(async () => {
	try {
		const response = await handleResponse(
			{},
			"http://127.0.0.1:5000/getresponse"
		);
		console.log("Response from handleResponse:", response);
	} catch (error) {
		console.error("Error in handleResponse:", error);
	}
})();

import { handleResponse } from "./server.js";

let inventory = {};

export async function createInventoryItem(name, amount) {
	const inventoryPopup = document.getElementById("inventory-popup");
	const itemContainer = inventoryPopup.querySelector(".item-container");
	if (inventory[name]) {
		inventory[name]["Item Amount"] += amount;

		const id = "#" + name.replace(/\s/g, "-");
		const itemDiv = itemContainer.querySelector(id);
		itemDiv.querySelector(".item-amount").innerHTML =
			"Item Amount: " + inventory[name]["Item Amount"];

		const itemAmount = Number(
			itemDiv.querySelector(".item-amount").innerHTML.split("Amount: ")[1]
		);
		if (itemAmount <= 0) {
			itemDiv.remove();
		}
	} else {
		const itemDiv = document.createElement("div");
		const itemName = document.createElement("span");
		itemName.innerHTML = "Item Name: " + name;
		itemName.className = "item-name";
		const itemAmount = document.createElement("span");
		itemAmount.innerHTML = "Item Amount: " + amount;
		itemAmount.className = "item-amount";
		itemDiv.appendChild(itemName);
		itemDiv.appendChild(itemAmount);
		itemDiv.classList.add("inventory-item", "panel");

		const id = name.replace(/\s/g, "-");
		itemDiv.id = id;

		inventory[name] = { "Item Name": name, "Item Amount": amount };

		return itemDiv;
	}
}

export async function updateInventory(response) {
	const inventoryPopup = document.getElementById("inventory-popup");
	const itemContainer = inventoryPopup.querySelector(".item-container");
	const inventoryUpdates = response["inventoryUpdates"];

	for (let i = 0; i < inventoryUpdates.length; i++) {
		const item = await createInventoryItem(
			inventoryUpdates[i]["name"],
			Number(inventoryUpdates[i]["changeAmount"])
		);

		if (item) {
			itemContainer.appendChild(item);
		}
	}
}

const inventoryPopup = document.getElementById("inventory-popup");

// Detect Change in Inventory
const observer = new MutationObserver((mutations) => {
	mutations.forEach((mutation) => {
		// Update Scroll Height
		if (mutation.removedNodes.length > 0) {
			const scrollingHeight = inventoryPopup.scrollHeight;
			const background = inventoryPopup.querySelector(".background");
			if (background) {
				background.style.height = scrollingHeight + "px";
			}
		}

		const scrollingHeight = inventoryPopup.scrollHeight;
		const background = inventoryPopup.querySelector(".background");
		if (background) {
			background.style.height = `${scrollingHeight}px`;
		}
	});
});

observer.observe(inventoryPopup, {
	attributes: true,
	childList: true,
	subtree: true,
});

// Open Inventory
document
	.getElementById("inventory-button")
	.addEventListener("click", function () {
		const inventoryPopup = document.getElementById("inventory-popup");
		if (inventoryPopup.style.display != "block") {
			inventoryPopup.style.display = "block";
			setTimeout(() => {
				inventoryPopup.style.height = "40vh";
				inventoryPopup.style.padding = "20px";
				inventoryPopup.style.borderWidth = "20px";
			}, 1);
		} else {
			inventoryPopup.style.height = "0";
			inventoryPopup.style.padding = "0px";
			inventoryPopup.style.borderWidth = "0px";
			setTimeout(() => {
				inventoryPopup.style.display = "None";
			}, 200);
		}
	});

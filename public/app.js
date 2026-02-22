import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, onAuthStateChanged, signOut, OAuthProvider, signInWithPopup } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore, collection, query, where, getDocs } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// TODO: Replace the following with your app's Firebase project configuration
// See: https://firebase.google.com/docs/web/learn-more#config-object
const firebaseConfig = {
  apiKey: "YOUR_API_KEY",
  authDomain: "YOUR_PROJECT_ID.firebaseapp.com",
  projectId: "YOUR_PROJECT_ID",
  storageBucket: "YOUR_PROJECT_ID.appspot.com",
  messagingSenderId: "YOUR_MESSAGING_SENDER_ID",
  appId: "YOUR_APP_ID"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// DOM Elements
const authContainer = document.getElementById('auth-container');
const appContainer = document.getElementById('app-container');
const userInfo = document.getElementById('user-info');
const userEmailDisplay = document.getElementById('user-email');
const logoutBtn = document.getElementById('logout-btn');

const authForm = document.getElementById('auth-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');
const authSubmitBtn = document.getElementById('auth-submit-btn');
const toggleAuthModeBtn = document.getElementById('toggle-auth-mode');
const msSsoBtn = document.getElementById('ms-sso-btn');
const authErrorDisplay = document.getElementById('auth-error');

const searchInput = document.getElementById('search-input');
const searchBtn = document.getElementById('search-btn');
const searchErrorDisplay = document.getElementById('search-error');
const loadingSpinner = document.getElementById('loading-spinner');
const resultsContainer = document.getElementById('results-container');
const resultsBody = document.getElementById('results-body');
const noResultsDiv = document.getElementById('no-results');

let isLoginMode = true;

// --- Authentication UI Logic ---
toggleAuthModeBtn.addEventListener('click', (e) => {
  e.preventDefault();
  isLoginMode = !isLoginMode;
  if (isLoginMode) {
    authSubmitBtn.textContent = 'Log In';
    toggleAuthModeBtn.textContent = 'Need an account? Register';
  } else {
    authSubmitBtn.textContent = 'Register';
    toggleAuthModeBtn.textContent = 'Already have an account? Log In';
  }
  authErrorDisplay.classList.add('d-none');
});

function showError(el, message) {
  el.textContent = message;
  el.classList.remove('d-none');
}

function clearError(el) {
  el.classList.add('d-none');
}

// --- Email/Password Auth ---
authForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  clearError(authErrorDisplay);
  const email = emailInput.value;
  const password = passwordInput.value;

  authSubmitBtn.disabled = true;
  authSubmitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';

  try {
    if (isLoginMode) {
      await signInWithEmailAndPassword(auth, email, password);
    } else {
      await createUserWithEmailAndPassword(auth, email, password);
    }
  } catch (error) {
    const errorCode = error.code;
    const errorMessage = error.message;
    showError(authErrorDisplay, `${errorCode}: ${errorMessage}`);
  } finally {
    authSubmitBtn.disabled = false;
    authSubmitBtn.textContent = isLoginMode ? 'Log In' : 'Register';
  }
});

// --- Microsoft SSO (Placeholder setup) ---
// Note: Requires enabling Microsoft provider in Firebase Console
msSsoBtn.addEventListener('click', async () => {
  const provider = new OAuthProvider('microsoft.com');
  // Optional: prompt="select_account" allows choosing account
  provider.setCustomParameters({
    prompt: 'select_account',
    // tenant: 'YOUR_TENANT_ID' // Enable this if limiting to specific tenant
  });

  try {
    await signInWithPopup(auth, provider);
  } catch (error) {
    console.error(error);
    showError(authErrorDisplay, error.message);
  }
});

// --- Auth State Observer ---
onAuthStateChanged(auth, (user) => {
  if (user) {
    // User is signed in.
    authContainer.classList.add('d-none');
    appContainer.classList.remove('d-none');
    userInfo.classList.remove('d-none');
    userInfo.classList.add('d-flex');
    userEmailDisplay.textContent = user.email || user.displayName || 'User';
  } else {
    // User is signed out.
    authContainer.classList.remove('d-none');
    appContainer.classList.add('d-none');
    userInfo.classList.add('d-none');
    userInfo.classList.remove('d-flex');
    // Clear search state on logout
    searchInput.value = '';
    resultsContainer.classList.add('d-none');
    noResultsDiv.classList.add('d-none');
    resultsBody.innerHTML = '';
  }
});

logoutBtn.addEventListener('click', () => {
  signOut(auth);
});

// --- Search Logic ---
searchBtn.addEventListener('click', performSearch);
searchInput.addEventListener('keypress', (e) => {
  if (e.key === 'Enter') performSearch();
});

async function performSearch() {
  const searchTerm = searchInput.value.trim().toUpperCase();
  clearError(searchErrorDisplay);
  
  if (!searchTerm) {
    showError(searchErrorDisplay, 'Please enter a search term.');
    return;
  }

  // Reset UI
  resultsContainer.classList.add('d-none');
  noResultsDiv.classList.add('d-none');
  loadingSpinner.classList.remove('d-none');
  resultsBody.innerHTML = '';

  try {
    const partsRef = collection(db, "parts");
    
    // We will perform up to 4 parallel queries because Firestore doesn't support generic 'OR' across multiple fields easily
    // We search the term in all 4 main fields.
    const queries = [
      query(partsRef, where("product_id_pcs", "==", searchTerm)),
      query(partsRef, where("product_id_triad", "==", searchTerm)),
      query(partsRef, where("distributor_part_number", "==", searchTerm)),
      query(partsRef, where("alternate_part_number", "==", searchTerm))
    ];

    const snapshots = await Promise.all(queries.map(q => getDocs(q)));
    
    // Combine results and deduplicate by document ID
    const resultsMap = new Map();
    snapshots.forEach(snapshot => {
      snapshot.forEach(doc => {
        resultsMap.set(doc.id, doc.data());
      });
    });

    const results = Array.from(resultsMap.values());

    loadingSpinner.classList.add('d-none');

    if (results.length === 0) {
      noResultsDiv.classList.remove('d-none');
    } else {
      renderResults(results);
      resultsContainer.classList.remove('d-none');
    }

  } catch (error) {
    console.error("Error searching:", error);
    loadingSpinner.classList.add('d-none');
    showError(searchErrorDisplay, `Search failed: ${error.message}`);
  }
}

function renderResults(results) {
  resultsBody.innerHTML = '';
  results.forEach(part => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="ps-4 fw-medium text-dark">${part.product_id_pcs || '-'}</td>
      <td>${part.product_id_triad || '-'}</td>
      <td>${part.distributor_part_number || '-'}</td>
      <td>${part.alternate_part_number || '-'}</td>
    `;
    resultsBody.appendChild(tr);
  });
}

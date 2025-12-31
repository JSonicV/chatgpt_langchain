# 05_pdf Frontend - SvelteKit Client

## Purpose

Client for a PDF chat app. Users can sign up, upload PDFs, view them, and chat
against a PDF. It also includes a scores page with bar charts.

## Entry Points and Files

- `05_pdf/client/src/routes/+layout.svelte` - app shell, navbar, error modal
- `05_pdf/client/src/routes/+page.svelte` - redirects to `/documents`
- `05_pdf/client/src/routes/documents/*` - list, upload, and detail pages
- `05_pdf/client/src/routes/chat/+page.svelte` - standalone chat page
- `05_pdf/client/src/routes/scores/+page.svelte` - scores page
- `05_pdf/client/src/routes/auth/*` - auth pages
- `05_pdf/client/src/api/axios.ts` - API wrapper
- `05_pdf/client/src/store/*` - Svelte stores
- `05_pdf/client/src/components/*` - reusable UI
- `05_pdf/client/static/spec.yaml` - OpenAPI spec for the backend

## Key UI Flow

1. Load `/documents` and fetch list of PDFs.
2. Upload a PDF and show progress.
3. Open `/documents/[id]` to see PDF viewer + chat panel.
4. Send messages via sync or streaming mode.
5. Score assistant responses via thumbs up/down.

## API Client

```ts
export const api = axios.create({
    baseURL: '/api'
});

api.interceptors.response.use(
    (res) => res,
    (err) => {
        if (err.response && err.response.status >= 500) {
            addError({
                contentType: response.headers['Content-Type'] || response.headers['content-type'],
                message: getErrorMessage(err)
            });
        }
        return Promise.reject(err);
    }
);
```
All API calls are routed through `/api` and server errors are pushed into the
global error store.

## Stores

### Auth store (`src/store/auth.ts`)
- `getUser`, `signin`, `signup`, `signout` methods
- `auth` writable store tracks `{ user, error, loading }`

### Document store (`src/store/documents.ts`)
- `upload` uses FormData and `api.post('/pdfs')`
- `uploadProgress` is updated via Axios `onUploadProgress`

### Error store (`src/store/errors.ts`)
Collects 5xx errors for the modal and lets the user dismiss them.

### Role enum (`src/store/role.ts`)
Maps chat roles to string values used by message rendering.

### Misc stores
- `src/store/store.ts` - example counter store
- `src/store/scores.ts` - commented-out scores store
- `src/store/chat/MessageOpts.ts` - empty placeholder

### Chat store (`src/store/chat/store.ts`)
Tracks conversations, active conversation, and message list.

```ts
const store = writable<ChatState>(INITIAL_STATE);

const insertMessageToActive = (message: Message) => {
    store.update((s) => {
        const conv = s.conversations.find((c) => c.id === s.activeConversationId);
        if (!conv) return;
        conv.messages.push(message);
    });
};
```
The custom `writable` from `src/store/writeable.ts` uses Immer so updates can
mutate state safely.

## Chat Send Modes

### Sync mode (`src/store/chat/sync.ts`)
```ts
const { data: responseMessage } = await api.post<Message>(
    `/conversations/${conversationId}/messages`,
    { input: message.content }
);
```
Adds a pending message, then replaces it with the server response.

### Streaming mode (`src/store/chat/stream.ts`)
```ts
const response = await fetch(`/api/conversations/${conversation.id}/messages?stream=true`, {
    method: 'POST',
    body: JSON.stringify({ input: userMessage.content }),
    credentials: 'include',
    headers: { 'Content-Type': 'application/json' }
});
```
Reads chunks from the response body and appends to the pending message.

## Components

- `ChatPanel.svelte` - wraps streaming toggle, conversation list, and input
- `ChatList.svelte` - renders messages by role
- `AssistantMessage.svelte` - displays Markdown + score controls
- `PdfViewer.svelte` - renders PDF pages via `pdfjs-dist`
- `ErrorModal.svelte` - displays captured server errors
- `Navbar.svelte`, `AuthLinks.svelte`, `FormGroup.svelte`, `TextInput.svelte` - auth UI
- `Alert.svelte`, `Progress.svelte`, `Button.svelte` - general UI helpers

### PDF Viewer snippet
```ts
const pdfDoc = await pdfjs.getDocument(url).promise;
for (let num = 1; num <= pdfDoc.numPages; num++) {
    pdfDoc.getPage(num).then(renderPage);
}
```
Each page is rendered to a canvas with a text layer overlay.

## Routes

- `/documents` - list PDFs
- `/documents/new` - upload form
- `/documents/[id]` - chat + PDF viewer
- `/scores` - charts from `/api/scores`
- `/auth/signin`, `/auth/signup`, `/auth/signout`
- `/chat` - standalone chat UI

## Data Loading (SvelteKit `load`)

`+page.ts` files call the API and return props for the page.

```ts
export const load = (async ({ params }) => {
    const {
        data: { pdf, download_url }
    } = await api.get(`/pdfs/${params.id}`);

    return {
        document: pdf,
        documentUrl: download_url
    };
}) satisfies PageLoad;
```
Errors are turned into `error` props using `getErrorMessage`.

## HTML, CSS, and Build Config

- `src/app.html` - loads pdf.js CSS and SvelteKit mount point
- `src/app.css` - Tailwind base + a custom `pre` style
- `svelte.config.js`, `vite.config.ts`, `tailwind.config.js` - build pipeline

## How-To Recipes

### Default streaming mode
`ChatPanel` reads `localStorage.getItem('streaming')`. Set a default:
```ts
let useStreaming = true;
```

### Add a new API call
Create a function in a store and call `api.get` or `api.post`. Handle errors
with `getErrorMessage` and update store state.

### Add a new page
Create a new folder under `src/routes` with `+page.svelte` and (optionally)
`+page.ts` for data loading.

### Display server errors
Use `addError` from `src/store/errors.ts` to push an error into the modal.

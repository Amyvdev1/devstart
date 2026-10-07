# DevStart Architecture

The app separates **scenario definitions**, **attempt evaluation**, and **benchmark aggregation**. The browser never decides whether an attempt is correct; it sends candidate inputs to the server and renders the returned contract.

Key design choice: failures are first-class educational states. Every failed attempt returns a status, stable error code, explanation, and next action rather than a generic “wrong answer.”

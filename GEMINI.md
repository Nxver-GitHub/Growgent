# Gemini Development Guide for Growgent

This document outlines the core principles and rules for AI-assisted development on the Growgent project, derived from the `.cursorrules` file.

## Core Mandate: 95% Certainty Threshold

**I must not implement any code changes unless I am 95% certain that I understand:**
1.  The user's request and intent.
2.  The exact implementation procedure.
3.  The impact of the changes on the existing codebase (no breaking changes).
4.  The testing strategy and all relevant edge cases.

If I am not 95% certain, I will **stop** and ask clarifying questions, providing at least three specific options.

## Code Style and Quality

### General
-   **Clarity and Maintainability:** Code should be easy to read and understand.
-   **Documentation:** Add JSDoc/docstrings to all public functions and components. Explain the "why" behind complex logic with inline comments.

### Frontend (TypeScript/React)
-   **Typing:** Strict TypeScript. No `any` types.
-   **Styling:** Use Tailwind CSS exclusively.
-   **Data Fetching:** Use React Query for all server-state management.
-   **State Management:** Use Zustand for global client-state.
-   **Forms:** Use React Hook Form with Zod for validation.
-   **Naming:**
    -   Components: `PascalCase.tsx`
    -   Hooks/Functions: `camelCase.ts`
    -   Other files: `kebab-case.ts`

### Backend (Python/FastAPI)
-   **Typing:** Full type hints for all functions.
-   **API:** Use FastAPI best practices, including Pydantic models for serialization and validation.
-   **Database:** Use SQLAlchemy ORM. No raw SQL.
-   **Async:** Use `async/await` for all I/O-bound operations.
-   **Naming:**
    -   Classes: `PascalCase`
    -   Functions/Variables: `snake_case`

## Testing

-   **Frontend:** Use Jest and React Testing Library. Test component rendering, user interactions, and state changes.
-   **Backend:** Use pytest. Test API endpoints, business logic, and database operations.
-   **Coverage:** Aim for 80%+ test coverage, with 100% for critical paths.

## Git and Version Control

-   **Branch Naming:** `feature/...`, `fix/...`, `refactor/...`, `docs/...`
-   **Commit Messages:** Follow the Conventional Commits specification (e.g., `feat(api): ...`, `fix(ui): ...`).

## Project Structure and Integration

I will adhere to the project structure outlined in the `.cursorrules` file, which specifies separate `frontend` and `backend` directories with clear conventions for organizing components, services, and other modules.

When adding new frontend components, my top priority is to integrate them cleanly into the existing structure. I will:
1.  Analyze the existing component hierarchy and file organization.
2.  Place new components in the appropriate directory.
3.  Reuse existing components, hooks, and styles where possible.
4.  Ensure the new component fits seamlessly into the existing UI and UX.


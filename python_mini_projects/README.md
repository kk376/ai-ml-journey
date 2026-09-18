# Python Mini Projects

Thirty small projects built using core Python concepts, I've learnt so far in my Python journey.

## Projects

### 01 — Password Strength Checker

Checks a password against five criteria (length, uppercase, lowercase, digits, special characters), scores it 0–5, and rates it as Weak, Medium, or Strong. Gives specific suggestions if the password falls short.

### 02 — Contact Book

A contact manager, where you can add, view, search, update, or delete contacts.

### 03 — Rock Paper Scissors

Play against the computer, which picks randomly from a list. Tracks wins, losses, and ties across multiple rounds.

### 04 — Quiz App

Multiple choice quiz with questions stored as a list of dictionaries. Shuffles the question order each run, gives feedback per question, and shows a final score with percentage.

### 05 — Calculator

Handles addition, subtraction, multiplication, division, modulus, and exponentiation. Catches division by zero. Loops until you quit.

### 06 — Student Grade Manager

Store students and their subject-wise scores. View all records, search by name, calculate class averages, or find top performers per subject.

### 07 — Word Frequency Counter

Write or paste some text and it counts how often each word appears. Displays the top N words in a formatted table.

### 08 — Shopping Cart

Browse a product catalog, add items to a cart, update quantities, remove items, and check out with a total.

### 09 — Expense Tracker

Log expenses with a description, amount, and category (picked from a tuple). View all entries, see spending grouped by category, check your top 5 expenses, set a monthly budget, and track how close you are to it.

### 10 — Number System Converter

Converts between decimal, binary, octal, and hex.

### 11: Todo List with File Storage

A persistent task manager supporting priority levels (High, Medium, Low), task categorization, completion timestamps, and full JSON file persistence.

### 12: Caesar Cipher Tool

Classical cryptography utility supporting text encryption, decryption with known shift keys, brute-force cracking across all 25 possible shifts, and direct text file processing.

### 13: Bank Account Simulator

Object-Oriented banking simulation featuring BankAccount and BankManager classes, transaction history auditing, custom exceptions (InsufficientFundsError, InvalidAmountError), and persistent JSON storage.

### 14: Inventory Management System

Warehouse inventory tracker with category tuples, stock adjustments, sale transactions with receipt generation, low-stock threshold alerts, valuation summaries, and CSV export.

### 15: Log File Analyzer

Diagnostic tool that parses server log files using regular expressions, calculates severity level distributions, extracts unique IP addresses using Python sets, and isolates errors.

### 16: Flashcard Study Tool

Interactive study application utilizing Python set operations to track mastered cards versus cards needing review, with category filtering and persistent JSON card decks.

### 17: Library Book Catalog

Object-Oriented library catalog using Book and LibraryCatalog classes, supporting title and author searching, book checkouts, returns, and catalog persistence.

### 18: Markdown to HTML Converter

Line-by-line Markdown parser converting headings, bold, italic, code blocks, unordered lists, and blockquotes into clean, styled HTML5 documents.

### 19: Health Metric Calculator

Health metric suite computing BMI with WHO category ratings, Basal Metabolic Rate (BMR), Daily Maintenance Calories (TDEE), and ideal body weight, with historical CSV logging.

### 20: Dungeon Adventure Game

Object-Oriented text adventure game with interconnected Room, Player, and Item classes, featuring inventory management, locked doors, hazards, and item interactions.

### 21: Unit Converter

Comprehensive multi-category measurement conversion tool supporting Length, Weight/Mass, Temperature (Celsius, Fahrenheit, Kelvin), Digital Storage (decimal and binary), and Speed with precision formatting.

### 22: URL Shortener Simulation

In-memory and JSON-backed URL shortening engine featuring Base62 encoding, custom alphanumeric alias registration, collision handling, and click counter analytics.

### 23: Typing Speed Tester

Terminal-based typing speed and accuracy evaluator measuring Gross WPM, Net WPM, Accuracy percentage, and CPM with randomized prompts and word-by-word diff error inspection.

### 24: File Deduplication Checker

High-performance duplicate file detection tool using multi-tier filtering (file size grouping, fast partial hashing, and streaming SHA-256 digests) to compute reclaimable disk storage.

### 25: Currency Exchange Calculator

Foreign exchange conversion engine with cross-rate calculation across major currencies, spread fee accounting, simulated multi-currency wallet management, and itemized receipt generation.

### 26: Sudoku Validator and Solver

9x9 Sudoku board validator and recursive backtracking constraint solver utilizing Minimum Remaining Values (MRV) candidate pruning for accelerated solving performance.

### 27: Simple HTTP API Server

RESTful JSON API server built purely with the Python standard library HTTPServer, supporting CRUD endpoints, query filtering, CORS headers, and status code governance.

### 28: System Metrics Monitor

Zero-dependency Linux procfs telemetrist directly parsing /proc/stat, /proc/meminfo, /proc/loadavg, and /proc/uptime with ASCII visual gauge bars.

### 29: LRU Cache Implementation

Classic O(1) Least Recently Used cache implemented from scratch using a Doubly Linked List and Hash Map, complete with capacity eviction policies and hit/miss telemetry.

### 30: Vector Math Toolkit

Pure Python 2D and 3D Euclidean vector algebra library with operator overloading for vector arithmetic, dot product, cross product, projections, and geometric angle computation.

## How to Run

Pick any file and run it:

```bash
python3 mini_project_name.py
```

All projects are terminal based and interactive.

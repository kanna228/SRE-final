// app/index.js
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

let todos = [];
let idSeq = 1;

// Health check endpoint
app.get('/health', (_req, res) => {
  res.json({ status: 'OK', timestamp: Date.now() });
});

// GET /todos – вывести все задачи
app.get('/todos', (_req, res) => {
  res.json(todos);
});

// POST /todos – создать новую задачу
app.post('/todos', (req, res) => {
  const { title } = req.body;
  if (!title) {
    return res.status(400).json({ error: 'title is required' });
  }
  const newTodo = { id: idSeq++, title };
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

// DELETE /todos/:id – удалить задачу
app.delete('/todos/:id', (req, res) => {
  const id = Number(req.params.id);
  const idx = todos.findIndex(t => t.id === id);
  if (idx === -1) {
    return res.status(404).json({ error: 'not found' });
  }
  todos.splice(idx, 1);
  res.status(204).end();
});

// Запуск сервера на порту 8080
const PORT = 8080;
app.listen(PORT, () => {
  console.log(`todo-app running on port ${PORT}`);
});

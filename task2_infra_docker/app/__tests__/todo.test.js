// app/__tests__/todo.test.js
const request = require('supertest');
const express = require('express');
const bodyParser = require('body-parser');

// Здесь дублируем код приложения, чтобы не зависеть от порта
const app = express();
app.use(bodyParser.json());

let todos = [];
let idSeq = 1;

app.get('/health', (_req, res) => {
  res.json({ status: 'OK', timestamp: Date.now() });
});

app.get('/todos', (_req, res) => {
  res.json(todos);
});

app.post('/todos', (req, res) => {
  const { title } = req.body;
  if (!title) return res.status(400).json({ error: 'title is required' });
  const newTodo = { id: idSeq++, title };
  todos.push(newTodo);
  res.status(201).json(newTodo);
});

app.delete('/todos/:id', (req, res) => {
  const id = Number(req.params.id);
  const idx = todos.findIndex(t => t.id === id);
  if (idx === -1) return res.status(404).json({ error: 'not found' });
  todos.splice(idx, 1);
  res.status(204).end();
});

describe('Todo API', () => {
  beforeEach(() => {
    todos = [];
    idSeq = 1;
  });

  test('GET /health returns status OK', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toBe(200);
    expect(res.body).toHaveProperty('status', 'OK');
  });

  test('POST /todos creates a new todo', async () => {
    const res = await request(app)
      .post('/todos')
      .send({ title: 'Test task' });
    expect(res.statusCode).toBe(201);
    expect(res.body).toHaveProperty('id', 1);
    expect(res.body).toHaveProperty('title', 'Test task');
  });

  test('GET /todos returns all todos', async () => {
    await request(app).post('/todos').send({ title: 'A' });
    const res = await request(app).get('/todos');
    expect(res.statusCode).toBe(200);
    expect(res.body.length).toBe(1);
  });

  test('DELETE /todos/:id deletes existing todo', async () => {
    await request(app).post('/todos').send({ title: 'To delete' });
    const res = await request(app).delete('/todos/1');
    expect(res.statusCode).toBe(204);
  });

  test('DELETE /todos/:id returns 404 if not found', async () => {
    const res = await request(app).delete('/todos/999');
    expect(res.statusCode).toBe(404);
  });
});

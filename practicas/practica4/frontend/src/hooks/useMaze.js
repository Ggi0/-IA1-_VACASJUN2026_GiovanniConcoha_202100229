// src/hooks/useMaze.js
// Hook central de estado del laberinto y resultados de búsqueda.
// Separa toda la lógica de estado de los componentes visuales.

import { useState, useCallback } from "react";
import * as api from "../services/api";

const EMPTY_RESULT = { bfs: null, dfs: null, comparison: null };

export function useMaze() {
  // ── Grid ──────────────────────────────────────────────────────────────────
  const [grid, setGrid] = useState([]);
  const [rows, setRows] = useState(10);
  const [cols, setCols] = useState(10);
  const [start, setStart] = useState(null);   // {row, col}
  const [end, setEnd] = useState(null);       // {row, col}
  const [density, setDensity] = useState(0.3);

  // ── Resultados ────────────────────────────────────────────────────────────
  const [results, setResults] = useState(EMPTY_RESULT);
  const [activeAlgo, setActiveAlgo] = useState(null); // "bfs" | "dfs" | "both"

  // ── UI state ──────────────────────────────────────────────────────────────
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [drawMode, setDrawMode] = useState("wall"); // "wall" | "start" | "end" | "erase"
  const [predefinedList, setPredefinedList] = useState([]);

  // ── Helpers internos ──────────────────────────────────────────────────────

  const mazePayload = useCallback(() => ({
    grid,
    start: { row: start?.row ?? 0, col: start?.col ?? 0 },
    end:   { row: end?.row   ?? rows - 1, col: end?.col   ?? cols - 1 },
  }), [grid, start, end, rows, cols]);

  const clearResults = () => setResults(EMPTY_RESULT);

  // ── Grid operations ───────────────────────────────────────────────────────

  /** Inicializa grid vacío de NxM */
  const initGrid = useCallback((r, c) => {
    const newGrid = Array.from({ length: r }, () => Array(c).fill(0));
    setGrid(newGrid);
    setRows(r);
    setCols(c);
    setStart({ row: 0, col: 0 });
    setEnd({ row: r - 1, col: c - 1 });
    clearResults();
  }, []);

  /** Alterna celda según drawMode */
  const toggleCell = useCallback((row, col) => {
    if (drawMode === "start") {
      setStart({ row, col });
      clearResults();
      return;
    }
    if (drawMode === "end") {
      setEnd({ row, col });
      clearResults();
      return;
    }
    setGrid((prev) => {
      const next = prev.map((r) => [...r]);
      if (drawMode === "wall")  next[row][col] = 1;
      if (drawMode === "erase") next[row][col] = 0;
      return next;
    });
    clearResults();
  }, [drawMode]);

  /** Limpia todas las paredes pero mantiene start/end */
  const clearWalls = useCallback(() => {
    setGrid((prev) => prev.map((r) => r.map(() => 0)));
    clearResults();
  }, []);

  // ── API calls ─────────────────────────────────────────────────────────────

  const withLoading = async (fn) => {
    setLoading(true);
    setError(null);
    try {
      await fn();
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const runBFS = () => withLoading(async () => {
    const res = await api.runBFS(mazePayload());
    setResults({ bfs: res, dfs: null, comparison: null });
    setActiveAlgo("bfs");
  });

  const runDFS = () => withLoading(async () => {
    const res = await api.runDFS(mazePayload());
    setResults({ bfs: null, dfs: res, comparison: null });
    setActiveAlgo("dfs");
  });

  const runBoth = () => withLoading(async () => {
    const res = await api.runBoth(mazePayload());
    setResults({ bfs: res.bfs, dfs: res.dfs, comparison: res.comparison });
    setActiveAlgo("both");
  });

  const loadPredefined = async (id) => withLoading(async () => {
    const maze = await api.getPredefined(id);
    setGrid(maze.grid);
    setRows(maze.grid.length);
    setCols(maze.grid[0].length);
    setStart(maze.start);
    setEnd(maze.end);
    clearResults();
  });

  const loadPredefinedList = async () => {
    try {
      const data = await api.listPredefined();
      setPredefinedList(data.mazes);
    } catch (e) {
      setError(e.message);
    }
  };

  const generate = () => withLoading(async () => {
    const maze = await api.generateMaze(rows, cols, density);
    setGrid(maze.grid);
    setStart(maze.start);
    setEnd(maze.end);
    clearResults();
  });

  const doExportCSV = () => withLoading(async () => {
    const payload = buildExportPayload();
    await api.exportCSV(payload);
  });

  const doExportPDF = () => withLoading(async () => {
    const payload = buildExportPayload();
    await api.exportPDF(payload);
  });

  const buildExportPayload = () => {
    if (results.bfs && results.dfs) {
      return { bfs: results.bfs, dfs: results.dfs, comparison: results.comparison };
    }
    return results.bfs || results.dfs;
  };

  const hasResults = results.bfs !== null || results.dfs !== null;

  return {
    // state
    grid, rows, cols, start, end, density, setDensity,
    results, activeAlgo, loading, error, setError,
    drawMode, setDrawMode, predefinedList,
    // actions
    initGrid, toggleCell, clearWalls,
    runBFS, runDFS, runBoth,
    loadPredefined, loadPredefinedList,
    generate, setRows, setCols,
    doExportCSV, doExportPDF,
    hasResults,
  };
}
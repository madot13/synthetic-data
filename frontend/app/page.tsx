"use client";
import { useState } from "react";
import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function SyntheticFactory() {
  const [prompt, setPrompt] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState("");
  const [filename, setFilename] = useState<string | null>(null);

  // --- Генерация новых данных ---
  const startGeneration = async () => {
    if (!prompt.trim()) return alert("Опишите, какие данные нужно сгенерировать");

    setLoading(true);
    setStatus("Запуск задачи...");

    try {
      const res = await axios.post(`${API_URL}/generate-tabular`, {
        prompt,
      });

      const taskId = res.data.task_id;
      setStatus("Генерация данных...");

      const interval = setInterval(async () => {
        const statusRes = await axios.get(`${API_URL}/task-status/${taskId}`);

        if (statusRes.data.status === "completed") {
          clearInterval(interval);
          setFilename(statusRes.data.result.filename);
          setStatus("Готово!");
          setLoading(false);
        }

        if (statusRes.data.status === "failed") {
          clearInterval(interval);
          setStatus("Ошибка генерации");
          setLoading(false);
        }
      }, 2000);

    } catch (err) {
      console.error(err);
      alert("Ошибка запуска задачи");
      setLoading(false);
    }
  };

  // --- Загрузка и дополнение CSV ---
  const uploadAndExtend = async () => {
    if (!uploadFile) return alert("Выберите CSV файл");

    setLoading(true);
    setStatus("Запуск задачи дополнения...");

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("prompt", prompt);
    formData.append("rows", "10"); // можно добавить поле для выбора

    try {
      const res = await axios.post(`${API_URL}/upload-and-extend`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const taskId = res.data.task_id;

      const interval = setInterval(async () => {
        const statusRes = await axios.get(`${API_URL}/task-status/${taskId}`);

        if (statusRes.data.status === "completed") {
          clearInterval(interval);
          setFilename(statusRes.data.result.filename);
          setStatus("Готово!");
          setLoading(false);
        }

        if (statusRes.data.status === "failed") {
          clearInterval(interval);
          setStatus("Ошибка генерации");
          setLoading(false);
        }
      }, 2000);

    } catch (err) {
      console.error(err);
      alert("Ошибка запуска задачи");
      setLoading(false);
    }
  };

  // --- Скачать CSV ---
  const downloadFile = () => {
    if (!filename) return;
    window.open(`${API_URL}/storage/results/${filename}`, "_blank");
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-slate-900 to-black text-white flex flex-col items-center py-16 px-6">
      <div className="max-w-4xl w-full bg-slate-800 rounded-2xl p-8 shadow-xl border border-slate-700">
        <h1 className="text-5xl font-extrabold mb-8 text-center text-gradient bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
          Synthetic Data Factory 🏭
        </h1>

        <p className="text-center text-slate-300 mb-6">
          Введите, какие данные хотите сгенерировать. <br />
          Пример: <em>"сгенерируй 10 строк с колонками имя, рост, вес, зарплата, должность"</em>
        </p>

        {/* --- Промпт для генерации --- */}
        <textarea
          className="w-full h-40 bg-slate-900 border border-slate-700 rounded-xl p-4 mb-4 placeholder-slate-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
          placeholder="Опишите данные..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
        />

        {/* --- Загрузка CSV --- */}
        <input
          type="file"
          accept=".csv"
          onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
          className="w-full bg-slate-900 border border-slate-700 rounded-xl p-2 mb-4"
        />

        {/* --- Кнопка генерации --- */}
        <button
          onClick={startGeneration}
          disabled={loading}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-blue-600 to-purple-600 hover:from-purple-600 hover:to-blue-600 transition-colors duration-300 font-bold text-lg shadow-lg mb-4"
        >
          {loading ? "Генерация..." : "Сгенерировать CSV"}
        </button>

        {/* --- Кнопка загрузки и дополнения --- */}
        <button
          onClick={uploadAndExtend}
          disabled={loading}
          className="w-full py-4 rounded-xl bg-gradient-to-r from-green-600 to-teal-600 hover:from-teal-600 hover:to-green-600 transition-colors duration-300 font-bold text-lg shadow-lg mb-4"
        >
          {loading ? "Дополнение..." : "Загрузить и дополнить CSV"}
        </button>

        {status && <p className="mt-4 text-center text-blue-400 font-medium">{status}</p>}

        {filename && (
          <button
            onClick={downloadFile}
            className="mt-6 w-full py-3 rounded-xl bg-emerald-600 hover:bg-emerald-500 transition-colors duration-200 font-semibold shadow-md"
          >
            Скачать {filename}
          </button>
        )}
      </div>
    </div>
  );
}
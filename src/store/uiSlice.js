import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    theme: localStorage.getItem("luxe-theme") || "light",
    lang: localStorage.getItem("luxe-lang") || "vi",
    collapsed: false,
  },
  reducers: {
    toggleTheme(state) {
      state.theme = state.theme === "dark" ? "light" : "dark";
      localStorage.setItem("luxe-theme", state.theme);
    },
    setLang(state, action) {
      state.lang = action.payload;
      localStorage.setItem("luxe-lang", state.lang);
    },
    setCollapsed(state, action) {
      state.collapsed = action.payload;
    },
  },
});

export const { toggleTheme, setLang, setCollapsed } = uiSlice.actions;
export default uiSlice.reducer;

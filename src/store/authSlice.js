import { createSlice } from "@reduxjs/toolkit";

const saved = (() => {
  try {
    return JSON.parse(localStorage.getItem("luxe-auth") || "null");
  } catch {
    return null;
  }
})();

const authSlice = createSlice({
  name: "auth",
  initialState: {
    token: saved?.token || null,
    user: saved?.user || null,
  },
  reducers: {
    setSession(state, action) {
      state.token = action.payload.token;
      state.user = action.payload.user;
      localStorage.setItem("luxe-auth", JSON.stringify(action.payload));
    },
    logout(state) {
      state.token = null;
      state.user = null;
      localStorage.removeItem("luxe-auth");
    },
  },
});

export const { setSession, logout } = authSlice.actions;
export default authSlice.reducer;

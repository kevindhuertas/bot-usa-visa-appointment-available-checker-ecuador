"use client";

import React from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";

// Paleta de colores principal
const primaryBlue = "#2196F3";       // Azul moderno y vibrante
const primaryBlueLight = "#64B5F6";  // Variante clara
const primaryBlueDark = "#1976D2";   // Variante oscura

// Ajuste de sombras más difuminadas
// Puedes seguir ajustando la opacidad y el spread para lograr
// el efecto de "blur" que desees.
const SHADOWS = [
  "none",
  "0 2px 4px rgba(0, 0, 0, 0.06)",
  "0 4px 8px rgba(0, 0, 0, 0.08)",
  "0 8px 16px rgba(0, 0, 0, 0.10)",
  "0 12px 24px rgba(0, 0, 0, 0.12)",
  ...Array(20).fill("none")
] as any;

const theme = createTheme({
  palette: {
    mode: "light",
    primary: {
      main: primaryBlue,
      light: primaryBlueLight,
      dark: primaryBlueDark,
      contrastText: "#fff",
    },
    secondary: {
      main: "#FF6B6B", 
      contrastText: "#fff",
    },
    background: {
      default: "#f8f9fa", // Fondo principal suave
      paper: "#ffffff",   // Fondo para contenedores (Paper)
    },
    text: {
      primary: "#2d3436", // Texto principal
      secondary: "#636e72", 
    },
    divider: "rgba(0, 0, 0, 0.08)",
  },
  typography: {
    fontFamily: [
      '"Inter"',
      '"Helvetica Neue"',
      'Arial',
      'sans-serif'
    ].join(','),
    h1: { 
      fontSize: "2.8rem", 
      fontWeight: 800,
      letterSpacing: "-0.03em",
      lineHeight: 1.2
    },
    h2: { 
      fontSize: "2.2rem", 
      fontWeight: 700,
      letterSpacing: "-0.02em",
      lineHeight: 1.3
    },
    h3: { 
      fontSize: "1.8rem", 
      fontWeight: 600,
      letterSpacing: "-0.01em",
      lineHeight: 1.4
    },
    body1: { 
      fontSize: "1rem",
      lineHeight: 1.6 
    },
    button: { 
      textTransform: "none", 
      fontWeight: 600,
      letterSpacing: "0.01em"
    },
  },
  shape: {
    borderRadius: 10,
  },
  components: {
    // ==== BOTONES ====
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          padding: "10px 24px",
          transition: "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
          "&:hover": {
            transform: "translateY(-1px)",
            boxShadow: SHADOWS[2],
          },
        },
        contained: {
          boxShadow: SHADOWS[1],
          "&:active": {
            boxShadow: SHADOWS[1],
          },
        },
        outlined: {
          borderWidth: 2,
          "&:hover": {
            borderWidth: 2,
            backgroundColor: "rgba(33, 150, 243, 0.04)"
          },
        },
        text: {
          "&:hover": {
            backgroundColor: "rgba(33, 150, 243, 0.05)",
            transform: "none",
          },
        },
      },
    },

    // ==== CARDS ====
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: SHADOWS[2],
          transition: "all 0.3s ease",
          "&:hover": {
            boxShadow: SHADOWS[3],
            transform: "translateY(-2px)",
          },
        },
      },
    },

    // ==== APP BAR ====
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: "rgba(255, 255, 255, 0.9)",
          backdropFilter: "blur(8px)",
          borderBottom: "1px solid rgba(0, 0, 0, 0.05)",
          boxShadow: SHADOWS[1],
        },
      },
    },

    // ==== TEXTFIELD ====
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            borderRadius: 8,
            "&.Mui-focused": {
              boxShadow: `0 0 0 2px ${primaryBlueLight}`,
            },
          },
          "& .MuiInputLabel-root.Mui-focused": {
            color: primaryBlue,
          },
        },
      },
    },

    // ==== CHIP ====
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 600,
          transition: "all 0.2s ease",
          "&.MuiChip-outlined": {
            borderWidth: 2,
            "&:hover": {
              backgroundColor: "rgba(33, 150, 243, 0.08)",
            },
          },
        },
      },
    },

    // ==== DIALOG ====
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 20,
          boxShadow: SHADOWS[3],
        },
      },
    },

    // ==== DIVIDER ====
    MuiDivider: {
      styleOverrides: {
        root: {
          backgroundColor: "rgba(0, 0, 0, 0.06)",
        },
      },
    },

    // ==== LIST ITEM BUTTON ====
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          "&:hover": {
            backgroundColor: "rgba(33, 150, 243, 0.04)",
          },
          "&.Mui-selected": {
            backgroundColor: "rgba(33, 150, 243, 0.08)",
          },
        },
      },
    },

    // ==== SWITCH ====
    MuiSwitch: {
      styleOverrides: {
        root: {
          padding: 8,
        },
        switchBase: {
          "&.Mui-checked": {
            color: "#fff",
            transform: "translateX(20px)",
          },
          "&.Mui-checked + .MuiSwitch-track": {
            backgroundColor: primaryBlue,
          },
        },
        track: {
          borderRadius: 14,
        },
        thumb: {
          width: 16,
          height: 16,
          boxShadow: "0 2px 4px rgba(0,0,0,0.1)",
        },
      },
    },

    // ==== PAPER (para que se note la sombra más difuminada) ====
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: SHADOWS[1], // Ajusta la sombra si quieres
          borderRadius: 16,
        },
      },
    },

    // ==== TABLAS (Table, TableHead, TableRow, etc.) ====
    MuiTableContainer: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: SHADOWS[2],
          overflow: "hidden", // Para que las esquinas redondeadas se vean
          backgroundColor: "#fff",
        },
      },
    },
    MuiTable: {
      styleOverrides: {
        root: {
          borderCollapse: "separate",
          borderSpacing: 0,
        },
      },
    },
    MuiTableHead: {
      styleOverrides: {
        root: {
          // Color de fondo de la cabecera
          backgroundColor: "#fafafa",
          "& th": {
            fontWeight: 600,
            borderBottom: `1px solid rgba(0, 0, 0, 0.08)`,
          },
        },
      },
    },
    MuiTableBody: {
      styleOverrides: {
        root: {
          // Ejemplo: quitar el borde de la última fila
          "& tr:last-of-type td": {
            borderBottom: 0,
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          borderBottom: `1px solid rgba(0, 0, 0, 0.08)`,
          padding: "16px",
        },
        head: {
          // Ajustes para las celdas de la cabecera
          fontSize: "0.875rem",
          fontWeight: 700,
          textTransform: "uppercase",
          color: "#2d3436",
        },
      },
    },
    MuiTableRow: {
      styleOverrides: {
        hover: {
          "&:hover": {
            backgroundColor: "rgba(33, 150, 243, 0.04)",
          },
        },
      },
    },
  },
});

const MuiThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {children}
    </ThemeProvider>
  );
};

export default MuiThemeProvider;

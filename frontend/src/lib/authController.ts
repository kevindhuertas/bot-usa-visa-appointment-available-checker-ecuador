// lib/authController.ts
export interface User {
    email: string;
    password: string;
    // Agrega otros campos que consideres necesarios
  }
  
  // Lista simulada de usuarios (se puede ampliar)
  const users: User[] = [
    { email: 'admin', password: '123456' },
    // Puedes agregar más usuarios de test
  ];
  
  /**
   * Simula el login.
   * Retorna una promesa que se resuelve con el usuario si las credenciales son válidas,
   * o se rechaza con un mensaje de error.
   */
  export const login = (email: string, password: string): Promise<User> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const user = users.find((u) => u.email === email && u.password === password);
        if (user) {
          resolve(user);
        } else {
          reject(new Error('Credenciales inválidas.'));
        }
      }, 500);
    });
  };
  
  /**
   * Simula el logout.
   */
  export const logout = (): Promise<void> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        resolve();
      }, 200);
    });
  };
  
  /**
   * Simula el reseteo de contraseña.
   * Se espera que se envíe una solicitud con el email y el administrador se pondrá en contacto.
   */
  export const resetPassword = (email: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      setTimeout(() => {
        const userExists = users.some((u) => u.email === email);
        if (userExists) {
          resolve();
        } else {
          reject(new Error('El usuario no existe.'));
        }
      }, 500);
    });
  };
  
import database
from app import App

if __name__ == "__main__":
    database.setup_database()

    app = App()
    app.mainloop()
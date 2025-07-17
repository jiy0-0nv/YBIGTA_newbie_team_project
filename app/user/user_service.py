from app.user.user_repository import UserRepository
from app.user.user_schema import User, UserLogin, UserUpdate

class UserService:
    def __init__(self, userRepoitory: UserRepository) -> None:
        self.repo = userRepoitory

    def login(self, user_login: UserLogin) -> User:
        ## TODO
        user = None
        return user
        
    def register_user(self, new_user: User) -> User:
        """
            Register a new user.
            Raises ValueError if the user already exists.
            
            Args:
                new_user (User): The user to register.
                
            Returns:
                User: The registered user.
        """
        if self.repo.get_user_by_email(new_user.email):
            raise ValueError("User already Exists.")
        
        new_user = self.repo.save_user(new_user)
        return new_user

    def delete_user(self, email: str) -> User:
        ## TODO        
        deleted_user = None
        return deleted_user

    def update_user_pwd(self, user_update: UserUpdate) -> User:
        ## TODO
        updated_user = None
        return updated_user
        
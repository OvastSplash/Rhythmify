from SpotifyController.services.database.data_builder import BuildDataService
from SpotifyController.services.client_services import UserClient, PublicClient
from SpotifyController.services.database.get_user_data import GetUserDataService
from SpotifyController.services.database.save_user_data import SaveUserDataService

from User.models import CustomUser
from typing import List

class BaseAggregator:
    def __init__(self) -> None:
        self.sp_db = BuildDataService()
        self.sp_public = PublicClient()

class BaseUserAggregator(BaseAggregator):
    def __init__(self, users: List[CustomUser]) -> None:
        super().__init__()
        self.users = users or []

    def run_services_for_each_user(self, *services: type['UserDataProcessor']) -> None:
        """
        Runs the provided services for each user in the users list.

        Raises an exception if the users list is empty. For each user, it initializes
        the given service classes, passing the current user and the parent instance
        to the service, and then executes their run method.

        Raises:
            Exception: If the users list is empty.

        Args:
            services: Variable number of service classes that implement
                'UserDataProcessor'. These classes will be instantiated and
                executed for each user.

        Returns:
            None
        """

        if not self.users:
            raise Exception("Users list is empty")

        for user in self.users:
            for service_cls in services:
                service = service_cls(parent=self, user=user)
                service.run()

class UserDataProcessor:
    def __init__(self, parent: BaseUserAggregator, user: CustomUser) -> None:
        self.parent = parent
        self.user = user
        self.sp_db = parent.sp_db
        self.sp_client = UserClient(self.user)
        self.user_db = SaveUserDataService(self.user)
        self.user_data = GetUserDataService(self.user)

    def run(self):
        raise NotImplementedError("Implement this class is subclass")
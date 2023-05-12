from django.urls    import path
from .views         import *

app_name    = "deaf_undead"

urlpatterns = [
    path(""                                         , SplashPageView.as_view()              , name="splash"                 ),
    path("home/"                                    , HomePageView.as_view()                , name="home"                   ),
    path("deaf/"                                    , DeafPageView.as_view()                , name="deaf"                   ),
    path("about/"                                   , AboutPageView.as_view()               , name="about"                  ),
    path("login/"                                   , NewUserLogin.as_view()                , name="login"                  ),
    path("detect/"                                  , DetectionPageView.as_view()           , name="detect"                 ),
    path("undeaf/"                                  , AnimationView.as_view()               , name="undeaf"                 ),
    path("search/"                                  , SearchPageView.as_view()              , name="search"                 ),
    path("logout/"                                  , NewUserLogout.as_view()               , name="logout"                 ),
    path("courses/"                                 , CoursesPageView.as_view()             , name="courses"                ),
    path("sign-up/"                                 , NewUserRegistration.as_view()         , name="signup"                 ),
    path("conversation/"                            , ConversationPageView.as_view()        , name="conversation"           ),
    path("inspirational/"                           , InspirationalPageView.as_view()       , name="ins"                    ),
    path("delete-account/"                          , DeleteCurrentAccount.as_view()        , name="del_acc"                ),
    path("forget-password/"                         , NewUserForgetPasswordView.as_view()   , name="forget_password"        ),
    path("change-password/"                         , NewUserChangePasswordView.as_view()   , name="change_password"        ),
    path("friendship/list/"                         , FriendShipListView.as_view()          , name="friendship_list"        ),
    path("course/<str:cat_name>/"                   , CourseDetailView.as_view()            , name="course"                 ),
    path("update-profile/<int:pk>"                  , NewUserUpdateProfile.as_view()        , name="update"                 ),
    path("friendship/create/<int:pk>/"              , FriendShipCreationView.as_view()      , name="create_friend"          ),
    path("manage-friendship/<int:fs_id>/"           , ManageFriendShipView.as_view()        , name="manage_friendship_list" ),
    path("reset-password/<str:email>/<str:token>/"  , NewUserResetPasswordView.as_view()    , name="reset_password"         ),
    path('course/<str:cat_name>/add-to-favorites/'  , AddToFavoritesView.as_view()          , name='add_to_favorites'       ),

]

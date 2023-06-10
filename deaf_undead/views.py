from django.views.generic       import TemplateView , CreateView , FormView , View , UpdateView
from django.contrib.auth.forms  import UserCreationForm , AuthenticationForm
from django.contrib.auth        import authenticate , login , logout
from django.shortcuts           import redirect , reverse , render
from django.http                import StreamingHttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views  import PasswordChangeView
from nltk.stem                  import WordNetLemmatizer
from difflib                    import get_close_matches
from keras.models               import model_from_json
from nltk.tokenize              import word_tokenize
from keras.layers               import LSTM , Dense
from keras.callbacks            import TensorBoard
from django.core.mail           import send_mail
from django.conf                import settings
from django.http                import Http404
from django.contrib.staticfiles import finders
from django.views               import View
from django.db.models           import Q
from .forms                     import *
from .models                    import *
from .utils                     import *
from .function                  import *
import cv2,nltk,enchant


class SplashPageView(TemplateView):
    template_name = "index.html"
    
class HomePageView(TemplateView):
    template_name = "home.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = self.request.user 
        context["new_current_user"] = NewUser.objects.get(user=current_user) 
        context["income_friends"  ] = FriendShip.objects.filter(to_user=context["new_current_user"],status='pending')      
        context["all_friends"     ] = FriendShip.objects.filter(from_user=context["new_current_user"],status="accepted")
        context["all_favs"        ] = FavouritCourses.objects.filter(user=context["new_current_user"])
        return context
   
class NewUserRegistration(CreateView):
    template_name   = "signup.html"
    form_class      = NewUserRegister
    success_url     = '/home/'
    def form_valid(self, form):
        username        = form.cleaned_data.get('username')
        password        = form.cleaned_data.get('password')
        email           = form.cleaned_data.get('email')
        first_name      = form.cleaned_data.get('first_name')
        last_name       = form.cleaned_data.get('last_name')
        user_type       = form.cleaned_data.get('user_type','on')
        user            = User.objects.create_user(username=username,
                                        email=email,
                                        password=password,
                                        first_name=first_name,
                                        last_name=last_name)
        form.instance.user = user
        login(self.request,user)
        return super().form_valid(form)
        
class NewUserLogin(FormView):
    template_name   = "login.html"
    form_class      = NewUserLogin
    success_url     = '/home/'
    message         = "There is an Login Error .. Please Try Again"
    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        usr      = authenticate(username=username,password=password)
        if usr is not None and NewUser.objects.filter(user=usr).exists():
            login(self.request,usr)
        else:
            return render(self.request,self.template_name,{'form':self.form_class,'message':self.message})
        return super().form_valid(form)
        
class NewUserLogout(View):
    def get(self,request):
        logout(request)
        return redirect('deaf_undead:login')
    
class NewUserUpdateProfile(UpdateView):
    model                   = NewUser
    form_class              = UpdateNewUserProfile
    template_name           = 'setting.html'
    success_url             = "/home/"
    def get_context_data(self, **kwargs):
        context             = super().get_context_data(**kwargs)
        current_user        = self.request.user 
        context["profile"]  = NewUser.objects.get(id=self.kwargs['pk'])
        return context

class NewUserForgetPasswordView(FormView):
    template_name       = "forget.html"
    form_class          = NewUserForgetPasswordForm
    success_url         = "/forget-password/?m=s"
    def form_valid(self, form):
        email           = form.cleaned_data.get('email')
        new_user        = NewUser.objects.get(user__email=email)
        user            = new_user.user
        url             = self.request.META['HTTP_HOST']
        message         = 'Please Check The Link Below To Reset Your Password.         '
        content         = url+"/reset-password/"+email+"/"+password_reset_token.make_token(user)+"/"
        send_mail(
            'Password Reset Link | SILENT PRESTO',
            message+content,
            settings.EMAIL_HOST_USER,
            [email],
            fail_silently = False,
        )
        return super().form_valid(form)

class NewUserResetPasswordView(FormView):
    template_name       = "change.html"
    form_class          = NewUserResetPasswordForm
    success_url         = "/login/"
    
    def dispatch(self, request, *args, **kwargs):
        email           = self.kwargs.get('email')
        new_user        = NewUser.objects.get(email=email)
        token           = self.kwargs.get('token')
        if new_user is not None and password_reset_token.check_token(new_user, token):
            pass
        # else:
        #     return redirect(reverse("deaf_undead:forget_password")+"?m=e")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        password        = form.cleaned_data['new_password']
        email           = self.kwargs['email']
        new_user        = NewUser.objects.get(email=email).user
        new_user.set_password(password)
        new_user.save()
        return super().form_valid(form)
        
class NewUserChangePasswordView(PasswordChangeView):
    template_name   = 'reset.html'
    success_url     =  '/home/'

class FriendShipCreationView(LoginRequiredMixin,CreateView):
    template_name               = "friendship_create.html"
    model                       = FriendShip
    fields                      = []
    
    def form_valid(self,form):
        current_user            = NewUser.objects.get(user=self.request.user)
        from_user               = current_user
        to_user                 = NewUser.objects.get(pk=self.kwargs['pk'])
        if from_user            == to_user:
            raise Http404("You can not send a friend request to yourself .. ")
        if FriendShip.objects.filter(from_user=from_user,to_user=to_user).exists():
            raise Http404("You have already sent a friend request to this user before ..")
        friendship              = form.save(commit=False)
        friendship.from_user    = from_user
        friendship.to_user      = to_user
        friendship.status       = 'pending'
        friendship.save()
        return redirect('deaf_undead:home')
    
class FriendShipListView(LoginRequiredMixin,TemplateView):
    template_name                   = "friends_list.html"
    def get_context_data(self, **kwargs):
        context                     = super().get_context_data(**kwargs)
        current_user                = NewUser.objects.get(user=self.request.user)
        context["all_friends"]      = FriendShip.objects.filter(from_user=current_user,status="accepted")
        context["income_friends"]   = FriendShip.objects.filter(to_user=current_user,status='pending') 
        context["outcome_friends"]  = FriendShip.objects.filter(from_user=current_user,status='pending') 
        users_income                = [u.from_user.user.username for u in context["income_friends"]]
        users_outcome               = [u.to_user.user.username for u in context["outcome_friends"]]
        my_friends                  = [u.to_user.user.username for u in context["all_friends"]]
        my_friends_zone             = users_income+users_outcome+my_friends
        context["last_users"]       = [us for us in NewUser.objects.all().exclude(user=self.request.user) if us.user.username not in my_friends_zone]
        return context

class ManageFriendShipView(View):
    def get(self,request,*args, **kwargs):
        friendship_id               = self.kwargs['fs_id']
        action                      = request.GET.get('action')
        friendship_obj              = FriendShip.objects.get(id = friendship_id)
        if action                   == 'acc':
            friendship_obj.status   = "accepted"
            FriendShip.objects.create(from_user=friendship_obj.to_user,to_user=friendship_obj.from_user,status="accepted")
            friendship_obj.save()
        elif action                 == 'dec':

            # FriendShip.objects.get(from_user=friendship_obj.to_user,to_user=friendship_obj.from_user).delete()
            FriendShip.objects.get(from_user=friendship_obj.from_user,to_user=friendship_obj.to_user).delete()
            friendship_obj.delete()

        else:
            pass
        return redirect('/home/')

class AboutPageView(TemplateView):
    template_name = "about.html"

class InspirationalPageView(TemplateView):
    template_name = "ins.html"
    
class CoursesPageView(TemplateView):
    template_name                   = "courses.html"
    def get_context_data(self, **kwargs):
        context                     = super().get_context_data(**kwargs)
        current_user                = self.request.user
        context["all_categories"]   = CoursesCategories.objects.all()
        context["new_current_user"] = NewUser.objects.get(user=current_user)
        context["all_favs"]         = [c.course.name for c in FavouritCourses.objects.filter(user=context["new_current_user"])]
        return context
'''
class DetectionPageView(View):
    cap = None 
    is_streaming = False
    def start_stream(self):
        self.is_streaming = True

    def stop_stream(self):
        self.is_streaming = False

    def stream(self):
        json_file = open("static/model.json", "r")
        model_json = json_file.read()
        json_file.close()
        
        model = model_from_json(model_json)
        
        model.load_weights("static/model.h5")
        
        sequence, sentence, accuracy, predictions, colors, threshold = [], [], [], [], [], 0.8
        
        for i in range(0, 20):
            colors.append((245, 117, 16))  # bgr   blue, gray , red

        def prob_viz(res, actions, input_frame, colors, threshold):
            output_frame = input_frame.copy()
            for num, prob in enumerate(res):
                cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), (90, 112, 134), -1)
                cv2.putText(output_frame, actions[num], (30, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,cv2.LINE_AA)
            return output_frame

        self.cap = cv2.VideoCapture(0)

        with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5,min_tracking_confidence=0.5) as hands:
            
            while self.cap.isOpened():
                _, frame = self.cap.read()
                            #       x      y
                cropframe = frame[0:640, 0:480]
                frame = cv2.rectangle(frame, (0, 40), (640, 480), (90, 112, 134), 2)
                
                image, results = mediapipe_detection(cropframe, hands)
                
                keypoints = extract_keypoints(results)
                
                sequence.append(keypoints)
                sequence = sequence[-15:]  
                try:
                    if len(sequence) == 15:
                        res = model.predict(np.expand_dims(sequence, axis=0))[0]
                        # max
                        predictions.append(np.argmax(res))
                        # 
                        if np.unique(predictions[-10:])[0] == np.argmax(res):
                            if res[np.argmax(res)] > threshold:
                                if len(sentence) > 0:
                                    if actions[np.argmax(res)] != sentence[-1]:
                                        sentence.append(actions[np.argmax(res)]) # A
                                        accuracy.append(str(round(res[np.argmax(res)] * 100, 2))) # 90%
                                else:
                                    sentence.append(actions[np.argmax(res)])
                                    accuracy.append(str(round(res[np.argmax(res)] * 100, 2)))

                        if len(sentence) > 1:
                            sentence = sentence[-1:]
                            accuracy = accuracy[-1:]
                except Exception as e:
                    pass
                text = f"            Output: - {' '.join(sentence)} ({' '.join(accuracy)}) %"
                cv2.rectangle(frame, (0, 0), (640, 40),(90, 112, 134), -1)
                cv2.putText(frame, text, (3, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        # cap.release()
        # cv2.destroyAllWindows()
    
    def __call__(self, *args, **kwargs):
        return self.stream(), 'multipart/x-mixed-replace; boundary=frame'

    def get(self,request):
        return StreamingHttpResponse(DetectionPageView().stream(), content_type='multipart/x-mixed-replace; boundary=frame')

    def post(self, request, *args, **kwargs):
        if 'start' in request.POST:
            self.start_stream()
        elif 'stop' in request.POST:
            self.stop_stream()
'''
def get_closest_valid_word(word):
    dictionary = enchant.Dict("en_US")
    closest_words = get_close_matches(word, dictionary.suggest, n=1, cutoff=0.8)
    if closest_words:
        return closest_words[0]
    return None

class DetectionPageView(View):
    cap = None 
    is_streaming = False

    def start_stream(self):
        self.is_streaming = True

    def stop_stream(self):
        self.is_streaming = False

    def stream(self):
        json_file = open("static/model.json", "r")
        model_json = json_file.read()
        json_file.close()

        model = model_from_json(model_json)
        model.load_weights("static/model.h5")

        sequence, sentence, accuracy, predictions, colors, threshold = [], [], [], [], [], 0.8
        high_accuracy_letters = []  # List to store letters with high accuracy

        for i in range(0, 20):
            colors.append((245, 117, 16))  # bgr   blue, gray , red

        def prob_viz(res, actions, input_frame, colors, threshold):
            output_frame = input_frame.copy()
            for num, prob in enumerate(res):
                cv2.rectangle(output_frame, (0, 60 + num * 40), (int(prob * 100), 90 + num * 40), (90, 112, 134), -1)
                cv2.putText(output_frame, actions[num], (30, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2,cv2.LINE_AA)
            return output_frame

        self.cap = cv2.VideoCapture(0)

        with mp_hands.Hands(model_complexity=0, min_detection_confidence=0.5, min_tracking_confidence=0.5) as hands:
            
            while self.cap.isOpened():
                _, frame = self.cap.read()
                cropframe = frame[0:640, 0:480]
                frame = cv2.rectangle(frame, (0, 80), (250, 440), (90, 112, 134), 2)
                
                image, results = mediapipe_detection(cropframe, hands)
                keypoints = extract_keypoints(results)
                
                sequence.append(keypoints)
                sequence = sequence[-15:]  
                try:
                    if len(sequence) == 15:
                        res = model.predict(np.expand_dims(sequence, axis=0))[0]
                        predictions.append(np.argmax(res))
                        
                        if np.unique(predictions[-10:])[0] == np.argmax(res):
                            if res[np.argmax(res)] > threshold:
                                if len(sentence) > 0:
                                    if actions[np.argmax(res)] != sentence[-1]:
                                        sentence.append(actions[np.argmax(res)])
                                        accuracy.append(str(round(res[np.argmax(res)] * 100, 2)))
                                        # Collect letters with high accuracy
                                        if res[np.argmax(res)] >= 0.8:
                                            high_accuracy_letters.append(actions[np.argmax(res)])
                                else:
                                    sentence.append(actions[np.argmax(res)])
                                    accuracy.append(str(round(res[np.argmax(res)] * 100, 2)))
                                    # Collect letters with high accuracy
                                    if res[np.argmax(res)] >= 0.8:
                                        high_accuracy_letters.append(actions[np.argmax(res)])
                        
                        if len(sentence) > 1:
                            sentence = sentence[-1:]
                            accuracy = accuracy[-1:]
                except Exception as e:
                    pass
                
                # text = f"Output: - {' '.join(sentence)} ({' '.join(accuracy)}) %"
                if len(high_accuracy_letters) > 1:
                    high_accuracy_letters = high_accuracy_letters[0:20]
                    text = f"""    (" {''.join(high_accuracy_letters).capitalize()} ") """
                    # text=f"{type(high_accuracy_letters)} - ({len(high_accuracy_letters)})"
                else:
                    text = ""
                cv2.rectangle(frame, (0, 0), (640, 40), (90, 112, 134), -1)
                cv2.putText(frame, text, (3, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 1, cv2.LINE_AA)
                _, jpeg = cv2.imencode('.jpg', frame)
                yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n\r\n')
        
    def __call__(self, *args, **kwargs):
        return self.stream(), 'multipart/x-mixed-replace; boundary=frame'

    def get(self,request):
        high_accuracy_word = ''  # Initialize with an empty word
        if self.is_streaming:
            high_accuracy_word = ''.join(high_accuracy_letters)
        response = StreamingHttpResponse(self.stream(), content_type='multipart/x-mixed-replace; boundary=frame')
        response.high_accuracy_word = high_accuracy_word  # Set the high_accuracy_word as an attribute of the response object
        return response

    def post(self, request, *args, **kwargs):
        if 'start' in request.POST:
            self.start_stream()
        elif 'stop' in request.POST:
            self.stop_stream()
              
class DeafPageView(TemplateView):
    template_name = "deaf.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        iframe_src = self.request.build_absolute_uri(reverse('deaf_undead:detect'))
        context["iframe_src"] = iframe_src
        return context

    def get(self, request, *args, **kwargs):
        detection_view = DetectionPageView()
        response = detection_view.get(request)
        high_accuracy_word = response.high_accuracy_word  # Get the high accuracy word
        context = self.get_context_data()
        context['high_accuracy_word'] = high_accuracy_word  # Add high accuracy word to the context
        return self.render_to_response(context)

    
class AnimationView(View):
    def get(self, request):
        return render(request, 'undeaf.html')

    def post(self, request):
        text                        = request.POST.get('sen')
        text.lower()
        words                       = word_tokenize(text)
        tagged                      = nltk.pos_tag(words)
        tense                       = {}
        tense["future"]             = len([word for word in tagged if word[1] == "MD"])
        tense["present"]            = len([word for word in tagged if word[1] in ["VBP", "VBZ", "VBG"]])
        tense["past"]               = len([word for word in tagged if word[1] in ["VBD", "VBN"]])
        tense["present_continuous"] = len([word for word in tagged if word[1] in ["VBG"]])
        stop_words                  = set(["mightn't", 're', 'wasn', 'wouldn', 'be', 'has', 'that', 'does', 'shouldn', 'do', "you've",
                                            'off', 'for', "didn't", 'm', 'ain', 'haven', "weren't", 'are', "she's", "wasn't", 'its',
                                            "haven't", "wouldn't", 'don', 'weren', 's', "you'd", "don't", 'doesn', "hadn't", 'is', 'was',
                                            "that'll", "should've", 'a', 'then', 'the', 'mustn', 'i', 'nor', 'as', "it's", "needn't",
                                            'd', 'am', 'have', 'hasn', 'o', "aren't", "you'll", "couldn't", "you're", "mustn't", 'didn',
                                            "doesn't", 'll', 'an', 'hadn', 'whom', 'y', "hasn't", 'itself', 'couldn', 'needn', "shan't",
                                            'isn', 'been', 'such', 'shan', "shouldn't", 'aren', 'being', 'were', 'did', 'ma', 't',
                                            'having', 'mightn', 've', "isn't", "won't"])

        lr                          = WordNetLemmatizer()
        filtered_text               = []
        for w, p in zip(words, tagged):
            if w not in stop_words:
                if p[1] == 'VBG' or p[1] == 'VBD' or p[1] == 'VBZ' or p[1] == 'VBN' or p[1] == 'NN':
                    filtered_text.append(lr.lemmatize(w, pos='v'))
                elif p[1] == 'JJ' or p[1] == 'JJR' or p[1] == 'JJS' or p[1] == 'RBR' or p[1] == 'RBS':
                    filtered_text.append(lr.lemmatize(w, pos='a'))
                else:
                    filtered_text.append(lr.lemmatize(w))

        words                       = filtered_text
        temp                        = []
        for w in words:
            if w == 'I':
                temp.append('Me')
            else:
                temp.append(w)
        words = temp  
        probable_tense = max(tense,key=tense.get) # acuracy hello 90%   olleh 10% 

        if probable_tense == "past" and tense["past"]>=1:
            temp                    = ["Before"]
            temp                    = temp + words
            words                   = temp
        elif probable_tense == "future" and tense["future"]>=1:
            if "Will" not in words:
                    temp            = ["Will"]
                    temp            = temp + words
                    words           = temp
            else:
                pass
        elif probable_tense == "present":
            if tense["present_continuous"]>=1:
                temp                = ["Now"]
                temp                = temp + words
                words               = temp


        filtered_text               = []
        for w in words:
            path                    = w + ".mp4"
            f                       = finders.find(path)
            #splitting the word if its animation is not present in database
            if not f:
                for c in w:
                    filtered_text.append(c)
            #otherwise animation of word
            else:
                filtered_text.append(w)
        words                       = filtered_text;
        return render(request, 'undeaf.html', {'words': words, 'text': text}) 
    
class SearchPageView(TemplateView):
    template_name                       = "search.html"
    def get_context_data(self, **kwargs):
        context                         = super().get_context_data(**kwargs)
        kw = self.request.GET.get("keyword")
        
        try:
            current_user                = NewUser.objects.get(user=self.request.user)
            context["all_friends"]      = FriendShip.objects.filter(from_user=current_user,status="accepted")
            context["income_friends"]   = FriendShip.objects.filter(to_user=current_user,status='pending') 
            context["outcome_friends"]  = FriendShip.objects.filter(from_user=current_user,status='pending')
            context['search_results']   = NewUser.objects.filter(Q(user__username__icontains=kw)|Q(first_name__icontains=kw)|Q(last_name__icontains=kw)).exclude(user=self.request.user)  
            
            for x in context['search_results']:
                for y in context["outcome_friends"]:
                    if x.user.username == y.to_user.user.username:
                        context["req"]="out"
            
            for x in context['search_results']:
                for y in context["income_friends"]:
                    if x.user.username == y.from_user.user.username:
                        context["req"]="in"
            
            for x in context['search_results']:
                for y in context["all_friends"]:
                    if x.user.username == y.to_user.user.username:
                        context["req"]="done"
            context["current_user"] = current_user
        except:
            context['search_results'] = ''
        return context
    
class ConversationPageView(TemplateView):
    template_name = "who.html"
    
class VideoFeedView(View):
    def get(self, request):
        cap = cv2.VideoCapture(0)
        
            
        def generate():
            with mp_hands.Hands(
                model_complexity=0,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5) as hands:
                while cap.isOpened():
                    ret, frame = cap.read()
                    cropframe=frame[40:400,0:400]
                    frame=cv2.rectangle(frame,(0,40),(400,400),255,2)
                    image, results = mediapipe_detection(cropframe, hands)
                    keypoints = extract_keypoints(results)
                    sequence.append(keypoints)
                    sequence = sequence[-15:]

                    try: 
                        if len(sequence) == 15:
                            res = model.predict(np.expand_dims(sequence, axis=0))[0]
                            print(actions[np.argmax(res)])
                            predictions.append(np.argmax(res))
                            if np.unique(predictions[-10:])[0]==np.argmax(res): 
                                if res[np.argmax(res)] > threshold: 
                                    if len(sentence) > 0: 
                                        if actions[np.argmax(res)] != sentence[-1]:
                                            sentence.append(actions[np.argmax(res)])
                                            accuracy.append(str(round(res[np.argmax(res)]*100,2)))
                                    else:
                                        sentence.append(actions[np.argmax(res)])
                                        accuracy.append(str(round(res[np.argmax(res)]*100,2))) 

                            if len(sentence) > 1: 
                                sentence = sentence[-1:]
                                accuracy=accuracy[-1:]
                    except Exception as e:
                        pass  
                    text = f"Output: - {' '.join(sentence)} ({' '.join(accuracy)}) %"
                    cv2.rectangle(frame, (0,0), (400, 40), (245, 117, 16), -1)
                    cv2.putText(frame,text, (3,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                    cv2.imshow('OpenCV Feed', frame)
                    if not ret:
                        break

                # Modify the frame here if needed
                # ...

                # Convert the frame to JPEG format
                _, jpeg = cv2.imencode('.jpg', frame)

                # Yield the frame in the HTTP response
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')
                cap.release()
                cv2.destroyAllWindows()
        # Set the MIME type of the HTTP response
        response = StreamingHttpResponse(generate(), content_type='multipart/x-mixed-replace; boundary=frame')
        return render(request, 'video_feed.html',{'response':response})

class CourseDetailView(TemplateView):
    template_name           = 'course.html'
    def get_context_data(self, **kwargs):
        context             = super().get_context_data(**kwargs)
        context['category'] = CoursesCategories.objects.get(name=self.kwargs['cat_name'])
        return context

class AddToFavoritesView(View):
    def get(self,request,*args, **kwargs):
        cat_name            = self.kwargs['cat_name']
        action              = request.GET.get('action')
        user                = NewUser.objects.get(user=self.request.user)
        course              = CoursesCategories.objects.get(name = cat_name)
        if action           == 'fav':
            if FavouritCourses.objects.filter(user=user,course=course).exists():
                pass
            else:
                FavouritCourses.objects.create(user=user,course=course)
        elif action         == 'del':
            if FavouritCourses.objects.filter(user=user,course=course).exists():
                FavouritCourses.objects.filter(user=user,course=course).delete()
            else:
                pass
        else:
            pass
        return redirect('/courses/')

class DeleteCurrentAccount(View):
    def get(self,request,*args, **kwargs):
        user = request.user
        NewUser.objects.get(user=user).delete()
        return redirect('/')
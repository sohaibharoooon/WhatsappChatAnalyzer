import os
import hashlib
from . import wca
import pandas as pd
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.storage import FileSystemStorage
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def WCA(request):
    if request.method == 'POST' and request.FILES.get('chat'):
        try:
            # ... [file handling logic remains same] ...
            chat_file = request.FILES['chat']
            #-------------file save------------
            fs = FileSystemStorage()
            def get_file_hash(file):
                hasher = hashlib.md5()
                for chunk in file.chunks():
                    hasher.update(chunk)
                return hasher.hexdigest()
        
            file_hash = get_file_hash(chat_file)
            file_path = os.path.join(settings.MEDIA_ROOT, f"{file_hash}.txt")

            if default_storage.exists(file_path):
                pass            
            else:
                with open(file_path, 'wb+') as destination:
                    for chunk in chat_file.chunks():
                        destination.write(chunk)                          
            # Read the file content
            with open(fs.path(file_path), 'r',encoding='utf-8') as f:
                file_content = f.read()
            A_data=chat_file.name
            # Now you can pass the content to your preprocessor or do something else        
            df_chat=wca.preprcessor(file_content)        
            users_list=df_chat['users'].unique().tolist()
            users_list.remove('group-notification')
            users_list.sort()
            users_list.insert(0,'Overall')
            df_chat=pd.DataFrame(df_chat)  
            #---------------fetch stats-------------- 
            Selected_user=request.POST.get("s_user","Overall")            
            total_messages,total_words,t_media,t_links,links,b_graph,wc_graph,mcw_plot,emoji_plot,emoji_df=wca.fetch_stats(df_chat,Selected_user)        
            s_df=wca.show_dataframe(df_chat)  
            MTL_Plot=wca.monthly_timeline(df_chat,Selected_user)
            DTL_Plot=wca.daily_timeline(df_chat,Selected_user) 
            mad=wca.most_active_day(df_chat,Selected_user)
            mam=wca.most_active_month(df_chat,Selected_user)
            activity_heatmap=wca.dt_heatmap(df_chat,Selected_user) 
            # Convert DataFrame to JSON-serializable format
            Wca_data = {
                'users': users_list,
                'name_data': A_data,
                'user_a': Selected_user,
                't_messages': total_messages,
                't_words': total_words,
                't_media': t_media,
                't_links': t_links,
                'links': links,
                # Convert all DataFrames to dict
                # 's_df': emoji_df.to_dict(),
                's_df': emoji_df,
                'df_chat': df_chat.to_dict(),
                # Add other plot data
                'b_graph': b_graph,
                'wc_graph': wc_graph,
                'mcw_plot': mcw_plot,
                'emoji_plot': emoji_plot,
                'MTL_Plot': MTL_Plot,
                'DTL_Plot': DTL_Plot,
                'mad': mad,
                'mam': mam,
                'activity_heatmap': activity_heatmap
            }
            return JsonResponse(Wca_data)
            # return render(request, 'wca4.html',Wca_data)            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'error': str(e)}, status=500)    
    return render(request, 'wca.html')
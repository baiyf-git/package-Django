import io
import os
import shutil
import tempfile
import zipfile

import yaml
from django.core.management.base import BaseCommand

from app_bot.minio_utils import MinIoClient
from app_bot.models import Intent  # 导入你要导出的模型
from app_bot.util import nlu_yml, response_yml, story_yml, domain_yml


class Command(BaseCommand):
    help = 'Export database data to a compressed zip file'

    # def add_arguments(self, parser):
    #     parser.add_argument('botId', type=int, help='Bot ID as a positional argument')

    def handle(self, *args, **options):
        bot_id = int(os.environ.get('BOT_ID', '1'))
        # 查询数据库获取数据
        queryset = Intent.objects.all()  # 替换为你的模型和查询

        # 创建一个临时目录来保存数据文件
        temp_dir = 'temp_data'
        os.makedirs(temp_dir, exist_ok=True)

        # 在临时目录中创建数据文件
        data_file = os.path.join(temp_dir, 'data.txt')
        with open(data_file, 'w') as f:
            for item in queryset:
                f.write(f'{item.name}, {item.example}\n')  # 替换为你的模型字段

        # 创建临时文件夹
        temp_dir = tempfile.mkdtemp()

        # 创建 "Data" 文件夹
        data_folder = os.path.join(temp_dir, "Data")
        os.makedirs(data_folder, exist_ok=True)

        # 生成YAML内容
        nlu_data = nlu_yml(bot_id)
        response_data, response_dict = response_yml(bot_id)
        story_data, rule_data = story_yml(bot_id)
        intents_data, entities_data, slots_data, action_data, form_slot_data = domain_yml(bot_id)

        # 将docs/config.yml的默认配置文件config.yml复制到临时文件夹中
        local_config = "app_bot/config.yml"
        temp_yaml_path = os.path.join(temp_dir, "config.yml")
        shutil.copy2(local_config, temp_yaml_path)

        # 将actions的默认配置文件action.py复制到临时文件夹中
        local_action = "app_bot/action_form_validation.py"
        temp_yaml_path = os.path.join(temp_dir, "action.py")
        shutil.copy2(local_action, temp_yaml_path)

        # domain.yml
        yaml_file_path = os.path.join(temp_dir, "domain.yml")
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(f'version: "3.1"\n\n')
            yaml_file.write(f'intents:\n')
            yaml_content = yaml.dump(intents_data, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

            yaml_file.write(f'\nentities:\n')
            yaml_content = yaml.dump(entities_data, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

            yaml_file.write('\nresponses:\n')
            for key, value in response_data.items():
                if isinstance(value, list):
                    yaml_file.write(f'  {key}:\n')
                    for item in value:
                        yaml_file.write(f'    - text: "{item}"\n')
                elif isinstance(value, dict):
                    yaml_file.write(f'  {key}:\n')
                    for sub_key, sub_value in value.items():
                        yaml_file.write(f'    - {sub_key}: "{sub_value}"\n')
            if len(response_dict) != 0:
                yaml_content = yaml.dump(response_dict, indent=2, sort_keys=False, allow_unicode=True)
                indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
                yaml_file.write(indented_yaml_str)

            yaml_file.write(f'\nslots:\n')
            yaml_content = yaml.dump(slots_data, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

            yaml_file.write(f'\nactions:\n')
            yaml_content = yaml.dump(action_data, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

            yaml_file.write(f'\nforms:\n')
            yaml_content = yaml.dump(form_slot_data, indent=2, sort_keys=False, allow_unicode=True)
            indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
            yaml_file.write(indented_yaml_str)

        # nlu.yml文件
        yaml_file_path = os.path.join(data_folder, "nlu.yml")
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(f'version: "3.1"\n')
            yaml_file.write('nlu:' + '\n')
            for nlu in nlu_data:
                yaml_file.write('- intent: ' + nlu["intent"] + '\n')
                yaml_file.write(f"  examples: |\n")
                for example in nlu["examples"]:
                    yaml_file.write('    - ' + example + '\n')

        # response.yml文件
        yaml_file_path = os.path.join(data_folder, "response.yml")
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(f'version: "3.1"\nresponses:\n')
            for key, value in response_data.items():
                if isinstance(value, list):
                    yaml_file.write(f'  {key}:\n')
                    for item in value:
                        yaml_file.write(f'    - text: "{item}"\n')
                elif isinstance(value, dict):
                    yaml_file.write(f'  {key}:\n')
                    for sub_key, sub_value in value.items():
                        yaml_file.write(f'    - {sub_key}: "{sub_value}"\n')
            if len(response_dict) != 0:
                yaml_content = yaml.dump(response_dict, indent=2, sort_keys=False, allow_unicode=True)
                indented_yaml_str = "\n".join("  " + line for line in yaml_content.splitlines())
                yaml_file.write(indented_yaml_str)

        # stories.yml文件
        yaml_file_path = os.path.join(data_folder, "stories.yml")
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(f'version: "3.1"\n')
            yaml_file.write('stories:' + '\n')
            for story in story_data:
                yaml_file.write('- story: ' + story["story"] + '\n')
                yaml_file.write('  steps:' + '\n')
                for key, value in story["steps"].items():
                    yaml_file.write('  - ' + key + ': ' + yaml.dump(value, default_style='plain', sort_keys=True,
                                                                    allow_unicode=True))

        # rules.yml文件
        yaml_file_path = os.path.join(data_folder, "rules.yml")
        with open(yaml_file_path, "w", encoding="utf-8") as yaml_file:
            yaml_file.write(f'version: "3.1"\nrules:\n')
            for rule in rule_data:
                yaml_file.write('- rule: ' + rule["rule"] + '\n')
                yaml_file.write('  steps:' + '\n')
                for key, value in rule["steps"].items():
                    yaml_file.write('  - ' + key + ': ' + yaml.dump(value, default_style='plain', sort_keys=True,
                                                                    allow_unicode=True))

        # 创建ZIP文件
        in_memory_zip = io.BytesIO()
        with zipfile.ZipFile(in_memory_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_root, _, filenames in os.walk(temp_dir):
                for filename in filenames:
                    file_path = os.path.join(folder_root, filename)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)

        # 检查桶是否存在
        minio_client = MinIoClient()
        if not minio_client.bucket_exists(bucket_name="bot"):
            minio_client.make_bucket(bucket_name="bot")

        zip_file_path = os.path.join(temp_dir, 'bot.zip')
        with open(zip_file_path, 'wb') as f:
            f.write(in_memory_zip.getvalue())
        object_name = f'{bot_id}/bot.zip'  # 指定在Minio中的对象名称

        # 上传文件到Minio
        minio_client.fput_object("bot", object_name, zip_file_path)

        # 删除临时文件夹
        shutil.rmtree(temp_dir)

        self.stdout.write(self.style.SUCCESS(f'Data exported to {zip_file_path}'))

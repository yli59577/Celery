from flask import Flask
from flask_restx import Api, Resource, fields
from celery_worker import add_task, celery_app

app = Flask(__name__)
api = Api(
    app,
    version='1.0.0',
    title='Celery ',
    description='使用 Celery 非同步計算 A+B 的 API',
    doc='/api' 
)


task_output = api.model('TaskOutput', {
    'task_id': fields.String(required=True, description='任務 ID')
})

add_input = api.model('AddInput', {
    'a': fields.Float(required=True, example=10, description='第一個數字'),
    'b': fields.Float(required=True, example=20, description='第二個數字')
})


result_output = api.model('ResultOutput', {
    'task_id': fields.String(required=True, description='任務 ID'),
    'status': fields.String(required=True, description='任務狀態'),
    'result': fields.Raw(description='計算結果', default=None)
})



@api.route('/echo/<string:text>')
class EchoResource(Resource):
    @api.marshal_with(task_output)
    @api.doc(description='使用 class-based task 回傳文字')
    def get(self, text):
        """呼叫 class-based task"""
        task = celery_app.send_task('tasks.echo_task_class', args=[text])
        return {'task_id': task.id}




@api.route('/add')
class AddResource(Resource):
    @api.expect(add_input)
    @api.marshal_with(task_output)
    @api.doc(description='使用裝飾器風格 task 計算 A+B')
    def post(self):
        """呼叫裝飾器風格 task 做加法"""
        data = api.payload
        task = add_task.apply_async(args=[data['a'], data['b']])
        return {'task_id': task.id}


@api.route('/task/<string:task_id>')
class TaskResultResource(Resource):
    @api.doc(description='查詢任務執行狀態與結果')
    def get(self, task_id):
        """查詢任務狀態"""
        task = celery_app.AsyncResult(task_id)
        
        response = {
            'task_id': task_id,
            'status': task.status,
            'result': None
        }
        
        if task.successful():
            response['result'] = task.result
        elif task.failed():
            response['result'] = str(task.result)
        
        return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
